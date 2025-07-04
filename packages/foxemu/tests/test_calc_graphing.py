import unittest

from foxemu.blocks.calc.block import Calc
from foxemu.blocks.calc.graphing import generate_dot
from foxemu.blocks.calc.parameters import CalcParameters
from pydot import Dot

if __name__ == "__main__":
    unittest.main()


class TestArithmetic(unittest.TestCase):
    def test_basics(self) -> None:
        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN RI01")
        parameters.STEP02.get_value().set("OUT RO02")
        parameters.STEP03.get_value().set("IN BI01")
        parameters.STEP04.get_value().set("OR BI02")
        parameters.STEP05.get_value().set("BIT 8")
        parameters.STEP06.get_value().set("IN 0")
        parameters.STEP07.get_value().set("GTO 29")
        parameters.STEP08.get_value().set("IN RI01")
        parameters.STEP09.get_value().set("BIZ 23")
        parameters.STEP10.get_value().set("IN RI04")
        parameters.STEP11.get_value().set("MUL M02")
        parameters.STEP12.get_value().set("ADD M01")
        parameters.STEP13.get_value().set("DIV RI01")
        parameters.STEP14.get_value().set("MUL M03")
        parameters.STEP15.get_value().set("STM M07")
        parameters.STEP16.get_value().set("SUB M08")
        parameters.STEP17.get_value().set("BIN 23")
        parameters.STEP18.get_value().set("IN M09")
        parameters.STEP19.get_value().set("SUB M07")
        parameters.STEP20.get_value().set("BIN 23")
        parameters.STEP21.get_value().set("IN M07")
        parameters.STEP22.get_value().set("GTO 29")
        parameters.STEP23.get_value().set("IN ~BI03")
        parameters.STEP24.get_value().set("OR ~BI04")
        parameters.STEP25.get_value().set("BIT 28")
        parameters.STEP26.get_value().set("IN M05")
        parameters.STEP27.get_value().set("GTO 29")
        parameters.STEP28.get_value().set("IN M06")
        parameters.STEP29.get_value().set("OUT RO01")
        parameters.STEP30.get_value().set("IN RI05")
        parameters.STEP31.get_value().set("SUB RI07")
        parameters.STEP32.get_value().set("STM M24")
        parameters.STEP33.get_value().set("IN RI05")
        parameters.STEP34.get_value().set("SUB RI06")
        parameters.STEP35.get_value().set("DIV M24")
        parameters.STEP36.get_value().set("LN")
        parameters.STEP37.get_value().set("STM M20")
        parameters.STEP38.get_value().set("IN RO02")
        parameters.STEP39.get_value().set("DIV M20")
        parameters.STEP40.get_value().set("STM M21")
        parameters.STEP41.get_value().set("MUL M04")
        parameters.STEP42.get_value().set("STM M22")
        parameters.STEP43.get_value().set("IN RO01")
        parameters.STEP44.get_value().set("MUL RO02")
        parameters.STEP45.get_value().set("DIV M22")
        parameters.STEP46.get_value().set("OUT RO03")
        parameters.STEP47.get_value().set("END")
        calc = Calc("TEST", "TEST", parameters)

        match generate_dot(calc):
            case Dot() as dot:
                print(dot.to_string())
