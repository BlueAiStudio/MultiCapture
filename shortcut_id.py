"""Sets the taskbar ID (System.AppUserModel.ID) of a Windows shortcut (.lnk), using only ctypes.
Used by install_shortcut.ps1 -Source, so that nothing has to be compiled (some managed PCs block that).
Run:  python shortcut_id.py <path to .lnk> <AppUserModelID>"""
import ctypes
import sys


class GUID(ctypes.Structure):
    _fields_ = [("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort), ("Data3", ctypes.c_ushort),
                ("Data4", ctypes.c_ubyte * 8)]


class PROPERTYKEY(ctypes.Structure):
    _fields_ = [("fmtid", GUID), ("pid", ctypes.c_ulong)]


class PROPVARIANT(ctypes.Structure):      # only the VT_LPWSTR case is used; size is right on 32 and 64 bit
    _fields_ = [("vt", ctypes.c_ushort), ("r1", ctypes.c_ushort), ("r2", ctypes.c_ushort), ("r3", ctypes.c_ushort),
                ("p", ctypes.c_void_p), ("p2", ctypes.c_void_p)]


def _guid(s):
    g = GUID()
    ctypes.oledll.ole32.CLSIDFromString(ctypes.c_wchar_p("{" + s + "}"), ctypes.byref(g))
    return g


def set_app_id(lnk, app_id):
    try:
        ctypes.oledll.ole32.CoInitialize(None)
    except OSError:
        pass                                   # already initialised in another mode: fine for this call
    ps = ctypes.c_void_p()
    iid = _guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")        # IID_IPropertyStore
    ctypes.oledll.shell32.SHGetPropertyStoreFromParsingName(ctypes.c_wchar_p(lnk), None, 2,   # GPS_READWRITE
                                                             ctypes.byref(iid), ctypes.byref(ps))
    vtbl = ctypes.cast(ctypes.cast(ps, ctypes.POINTER(ctypes.c_void_p))[0], ctypes.POINTER(ctypes.c_void_p))
    release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtbl[2])
    set_value = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(PROPERTYKEY),
                                   ctypes.POINTER(PROPVARIANT))(vtbl[6])
    commit = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(vtbl[7])
    key = PROPERTYKEY(_guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"), 5)   # PKEY_AppUserModel_ID
    text = ctypes.create_unicode_buffer(app_id)
    value = PROPVARIANT(vt=31, p=ctypes.cast(text, ctypes.c_void_p))   # VT_LPWSTR
    try:
        set_value(ps, ctypes.byref(key), ctypes.byref(value))
        commit(ps)
    finally:
        release(ps)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    set_app_id(sys.argv[1], sys.argv[2])
    print("AppUserModelID set:", sys.argv[2])
