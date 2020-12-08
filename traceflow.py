import sys
import json
from utils import *
from androguard import *
from androguard import misc
from androguard import session
from androguard.core.bytecode import *
from androguard.core.bytecodes.apk import *
from androguard.core.analysis.analysis import *
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat
from androguard.core.analysis.analysis import Analysis
from androguard.decompiler.decompiler import DecompilerJADX
from androguard.misc import AnalyzeAPK
from androguard.core.androconf import show_logging
import logging
import re
from collections import OrderedDict



class TraceFlow:
    def __init__(self):
        self.find_list = ["startActivity","startService"]
        self.act_change = []
        self.Log_list = []

    def getLogger(self):
        __log = logging.getLogger("TraceFlow")
        __log.setLevel(logging.DEBUG)
        stream_hander = logging.StreamHandler()
        stream_hander.setLevel(logging.DEBUG)
        __log.addHandler(stream_hander)
        file_handler = logging.FileHandler('my.log')
        file_handler.setLevel(logging.CRITICAL)
        __log.addHandler(file_handler)
        self.logger = __log
        return __log

    def search(self, path, method,dept):
        #종결 조건
        if(method.is_external() or method.is_android_api()):
            self.logger.critical("["+str(dept)+"]"+"EXTERNAL OR API")
            return

        if(method.name == "<init>"):
            self.logger.critical("["+str(dept)+"]"+"INIT_END")
            return
        #if(method.name == "isPrimaryNavigation" or method.name == "getFragmentFactory" or method.name == "setFragmentFactory"):
        #    return
        for meth in method.get_xref_to():
            tmp_path = path
            tmp_path.append(str(self.extract_class_name(meth[0].name)) + "::" + str(meth[1].name))
            if(meth[1].name in self.find_list):#너비 우선 탐색으로 변경
                self.logger.critical("---Find!---")
                connect_activity = self.methodAnalysis(method)
                if connect_activity == None:
                    return

                path.append(self.extract_class_name(str(meth[0].name))+"::"+str(meth[1].name))
                self.Log_list.append(path)
                self.logger.critical("\n\n------New Activity Found!-----\n\n"+connect_activity)
                for cls in self.dx.find_classes(connect_activity):
                    self.logger.critical("\n\n---------Root Class-----------------\n"+str(cls.name))
                    for methd in dx.find_methods(cls.name,"^onCreate$"):
                        if(methd.name == "onCreate"):
                            self.logger.critical(str(methd.name))
                            path.append(self.extract_class_name(cls.name)+'::'+methd.name)
                            self.search(tmp_path, methd, 0)
            if method.name == meth[1].name:
                self.logger.critical("Loop!")
                continue
            self.logger.critical("["+str(dept)+"]"+"INSIDE: " + str(meth[0].name) + "::" + str(meth[1].name))
            self.logger.info("Full path" + toString(tmp_path))
            self.search(tmp_path, meth[1], dept+1)

    def traceMethod(self, dx, startPoint, table):
        if table == None:
            self.dx = dx#제거
            clslist = dx.find_classes(startPoint)
            for cls in clslist:
                self.logger.critical("\n\n---------Root Class-----------------\n"+str(cls.name))
                self.logger.info(cls.name)
                for meth in cls.get_methods():
                    self.logger.info(meth.name)
                    tmp_path = [str(cls.name) + "::" + str(meth.name)]
                    self.logger.critical(str(meth.name))
                    self.search(tmp_path, meth, 0)
            self.logger.info("end of stream")
    def traceAct(self, dx, startPoint):
        self.dx = dx#제거
        classlist = dx.find_classes("^"+FormatClassToJava(startPoint)+"$")
        tmp_act_path = []
        for cls in classlist:
            fmethod = dx.find_methods(cls.name,"^onCreate$")
            for me in fmethod:
                if(me.name == "onCreate"):
                    tmp_act_path.append(self.extract_class_name(cls.name)+"::"+me.name)
                    self.search( tmp_act_path,me,0)

    def extract_class_name(self, dir_class):
        tmp=dir_class.split('/')
        class_name = tmp.pop()
        return class_name

    def methodAnalysis(self, meth):
        
        if meth.is_external() or meth.is_android_api():
            return
        meth = meth.get_method()
        searchdata = meth.get_source()
        regex = re.compile('Intent\(.*?\)\,(.*[a-z])\)')

        test_str = searchdata

        match=regex.search(test_str)
        return FormatClassToJava(match.group(1).lstrip())
            
                    
#내일 할일 startActivity를 찾았을 때 어떤 class로 던지는지를 찾아야함 ㅇㅇ이거 가능하나 ? ㅋㅋㅋ
            
            