#pragma once

int* get_errno_addr();
#define errno (*get_errno_addr())
