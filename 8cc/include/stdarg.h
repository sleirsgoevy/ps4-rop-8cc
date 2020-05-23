#ifndef ELVM_LIBC_STDARG_H_
#define ELVM_LIBC_STDARG_H_

typedef long long* va_list;

#define va_start(l, x) ((l) = (long long*)&(x))
#define va_arg(l, tp) (*(tp*)++(l))
#define va_copy(l1, l2) ((l1) = (l2))
#define va_end(l)

#define __gnuc_va_list va_list
#define _VA_LIST_DEFINED
#endif
