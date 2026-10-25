# Black-box: this host's errno numbers for stdio.c:59-94's 26 names.
import errno, os, platform
names = ("EACCES EAGAIN EBADF EBUSY EEXIST EFAULT EFBIG EINTR EINVAL EIO EISDIR "
         "ELOOP EMFILE ENAMETOOLONG ENFILE ENODEV ENOENT ENOMEM ENOSPC ENOTDIR "
         "ENOTEMPTY EOVERFLOW EPERM EROFS ESPIPE EXDEV").split()
print("# host:", platform.system(), platform.machine(), platform.release())
for n in names:
    print(n, getattr(errno, n), os.strerror(getattr(errno, n)))
