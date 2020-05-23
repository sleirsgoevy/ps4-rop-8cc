all: make-8cc make-bh build/syscall_names.txt

make-8cc:
	cd 8cc; make

make-bh:
	cd bad_hoist; make

build/syscall_names.txt: bad_hoist/dumps/syscalls.txt
	mkdir -p build
	python3 scripts/syscall_names.py < bad_hoist/dumps/syscalls.txt > build/syscall_names.txt

clean:
	cd 8cc; make clean
	cd bad_hoist; make clean
	rm -rf build
