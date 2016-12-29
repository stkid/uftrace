#!/usr/bin/env python

from runtest import TestBase

class TestCase(TestBase):
    def __init__(self):
        TestBase.__init__(self, 'lib', """
# DURATION    TID     FUNCTION
            [17458] | lib_a(4095) {
            [17458] |   lib_b(4096) {
   5.193 us [17458] |     lib_c(4095);
   6.911 us [17458] |   } /* lib_b */
   8.279 us [17458] | } /* lib_a */
""", sort='simple')

    def build(self, name, cflags='', ldflags=''):
        import os
        import subprocess as sp

        if self.lang not in TestBase.supported_lang:
#            print("%s: unsupported language: %s" % (self.name, self.lang))
            return TestBase.TEST_UNSUPP_LANG

        lang = TestBase.supported_lang[self.lang]
        prog = 't-' + self.name

        build_cflags  = ' '.join(TestBase.default_cflags + [self.cflags, cflags, \
                                  os.getenv(lang['flags'], '')])
        build_ldflags = ' '.join([self.ldflags, ldflags, \
                                  os.getenv('LDFLAGS', '')])

        # cygprof doesn't support arguments now
        if build_cflags.find('-finstrument-functions') >= 0:
            return TestBase.TEST_SKIP

        lib_cflags = build_cflags + ' -shared -fPIC'

        # build libabc_test_lib.so library
        build_cmd = '%s -o libabc_test_lib.so %s s-lib.c %s' % \
                    (lang['cc'], lib_cflags, build_ldflags)

#        print("build command for library: %s" % build_cmd)
        if sp.call(build_cmd.split(), stdout=sp.PIPE) < 0:
            return TestBase.TEST_BUILD_FAIL

        exe_ldflags = build_ldflags + ' -Wl,-rpath,$ORIGIN -L. -labc_test_lib'

        build_cmd = '%s -o %s s-libmain.c %s' % \
                    (lang['cc'], prog, exe_ldflags)

#        print("build command for executable: %s" % build_cmd)
        if sp.call(build_cmd.split(), stdout=sp.PIPE) < 0:
            return TestBase.TEST_BUILD_FAIL
        return 0

    def runcmd(self):
        return '%s --force --no-libcall -A ^lib@libabc_test,arg1 %s' % (TestBase.ftrace, 't-' + self.name)
