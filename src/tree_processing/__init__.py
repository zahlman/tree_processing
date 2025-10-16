from os import link


# Path.hardlink_to requires 3.10.
# For better compatibility, we fall back to the os module
# and also fall back on copying if hardlinks fail for any reason.
def hardlink_or_copy(src, dst):
    try:
        link(src, dst)
    except:
        copy(src, dst)
