#!/usr/bin/python3
# -*- coding: UTF-8 -*-

__author__ = "chenxh"

from ...FileUtils import FileHelper
import json, struct
from .DataTypeTranslator import *

class BatchTable:
    '''
    3dtiles每个tile数据文件的batchtable数据
    '''
    DEFAULT = {
        "BatchTable.JSON": {},
        "BatchTable.Binary": {}
    }
    def __init__(self, tableType:str, btJSONBuffer:bytes, btBinaryBuffer:bytes, batchLength:int):
        self.tableType = tableType
        self.btJSON = _BtJSON(tableType, btJSONBuffer)
        self.btBinary = _BtBinary(tableType, btBinaryBuffer, self.btJSON.json, batchLength)

    def toDict(self):
        return {
            "BatchTable.JSON": self.btJSON.toDict(),
            "BatchTable.Binary": self.btBinary.toDict()
        }

class _BtJSON:
    def __init__(self, tableType:str, bufferData:bytes):
        self.tableType = tableType
        # 如果bufferData是b''，返回的应该是空JSON（字典）
        self.json = {}
        if len(bufferData) != 0:
            self.json = json.loads(FileHelper.bin2str(bufferData))
        # self.isRefBinaryBody = False # 备用

    def toDict(self):
        return self.json

class _BtBinary:
    def __init__(self, tableType:str, bufferData:bytes, btJSON:dict, batchLength:int):
        self.tableType = tableType
        self.btJSON = btJSON
        self.data = {}

        if len(bufferData) == 0:
            return
        else:
            if tableType == 'b3dm':
                offset = 0
                for batchId in btJSON:
                    # 获取batch组件类型和batch组件的元素数量
                    componentType = btJSON[batchId]["componentType"]
                    _type = btJSON[batchId]["type"]

                    # 获取batch组件对应的python解构格式和字节长度
                    fmtStr, bytesize = getCTypeFmtStr(componentType)
                    # 获取当前batchId组件的二进制解构格式字符串
                    componentCount = getCmptCount(_type)
                    fmt = str(batchLength * componentCount) + fmtStr
                    
                    # 解构成字符串，并传递给self的data字典
                    self.data[batchId] = struct.unpack(fmt, bufferData[offset:offset + batchLength * componentCount * bytesize])
                    
                    # 继续为下一个batchId偏移到起点
                    offset += batchLength * componentCount * bytesize

            if tableType == 'pnts':
                pass

    def toDict(self):
        return self.data
