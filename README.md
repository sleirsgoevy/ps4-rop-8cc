# ps4-rop-8cc

This is a port of shinh's [ELVM branch of 8cc](https://github.com/shinh/8cc/tree/eir) to the PS4 return-oriented programming. It runs C code on OFW 6.51 (EDIT: 6.72 confirmed to be working too) via [Fire30's WebKit exploit](https://github.com/Fire30/bad_hoist).

## Building

Simply run `make` and follow the instructions to setup the toolchain.

## Running

A reference script, `scripts/run.py`, is provided.

`python3 scripts/run.py file1.c [file2.c]...`

Look at its source code if you want more precise control over what's happening.

## ABI

ELVM/x64 register mapping:

```
ELVM    x64     notes
A       rax
B       rcx
C       r10
D       --      the compiler never uses the D register
SP      rdi     rsp is used for the ropchain, so the stack has to be emulated
BP      r8
```

The compiler has been modified so that memory addressing and type sizes are the same as in native code. This allows native headers (e.g. from [OpenOrbis SDK](https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain)) to be included directly.

The calling convention is essentially CDECL, with `call` being implemented as `push next ; jmp func ; next:`. That is, `SP` (`rdi`) points to the return address on function entry. The result is returned in `B` (`rcx`).

The compiler detects whether a given function call is a rop-to-rop or rop-to-native call, and converts the calling convention if necessary. For native-to-rop calls the conversion has to be performed explicitly:

```
#include <librop/extcall.h>

void native_func(..., void(*)(...), void* opaque, ...);
void my_very_func(void* opaque, ...); // only this format is supported

...

extcall_t ec;
char stack[8192]; // emulated stack to be used by my_very_func
create_extcall(ec, my_very_func, stack + 8192, opaque);
native_func(..., extcall_gadget, ec, ...);
```

To call a native function pointer, you must call `rop_call_funcptr` or implement the same functionality yourself:

`rop_call_funcptr(ptr_to_printf, "Hello, %s!\n", "world");`

Note: there is a ready-to-use wrapper for `pthread_create` in `librop/pthread_create.h` that will perform the conversion for you.

## Speed

This is no speed demon. `8cc` compiles the C code to a stack machine, and is is then run on a software-emulated stack. The use of ROP further slows things down by essentially disabling CPU branch prediction. The end result is that an empty `for` loop does about 1e6 iterations per second.

## Known bugs

* ~~Code using global or static variables won't compile. Use `mmap` if you are not happy with 64KB of stack.~~ Probably fixed.
* The constant-parsing code stores constants as `int` internally. This means that 64-bit constants won't work.
* 64-bit integer comparison is always signed.
* Arithmetic shift right is not supported (yet).
* The generated ROP is reentrant but not thread-safe. That is, one ROP function can only be called on a single thread. This does not apply to rop-to-native calls.
* Although the toolchain uses full FreeBSD headers, only the functions that map 1:1 to system calls can be used.
