import unittest
from collections.abc import Iterable

from foxemu.blocks.calc.block import Calc
from foxemu.blocks.calc.parameters import CalcParameters
from foxemu.emulator import Emulator
from foxemu.signaling import Parameter, RealValue

if __name__ == "__main__":
    unittest.main()


def execute_with_assertions(
    test: unittest.TestCase,
    parameters: CalcParameters,
    assertions: Iterable[tuple[Parameter, float]],
) -> Calc:
    parameters.NAME.get_value().set("TEST")
    calc = Calc("TEST", "TEST", parameters)
    emulator = Emulator()
    emulator.add_block(calc)
    emulator.execute()

    for a, b in assertions:
        test.assertEqual(a.get_value().get(), b)

    return calc


class TestArithmetic(unittest.TestCase):
    def test_basics(self) -> None:
        parameters = CalcParameters()
        parameters.M01.get_value().set(1 + 1 / 9)
        parameters.M02.get_value().set(1 + 1 / 3)
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("IN 1")
        parameters.STEP03.get_value().set("ADD")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("IN 1")
        parameters.STEP06.get_value().set("IN 1")
        parameters.STEP07.get_value().set("IN 1")
        parameters.STEP09.get_value().set("ADD 3")
        parameters.STEP10.get_value().set("OUT RO02")
        parameters.STEP11.get_value().set("IN M01")
        parameters.STEP12.get_value().set("ADD M02")
        parameters.STEP13.get_value().set("OUT RO03")
        parameters.STEP14.get_value().set("IN 10")
        parameters.STEP15.get_value().set("DEC")
        parameters.STEP16.get_value().set("STM M11")
        parameters.STEP17.get_value().set("DEC 3")
        parameters.STEP18.get_value().set("STM M12")
        parameters.STEP19.get_value().set("STM M13")
        parameters.STEP20.get_value().set("DEC M13")
        parameters.STEP21.get_value().set("INC")
        parameters.STEP22.get_value().set("STM M14")
        parameters.STEP23.get_value().set("INC 3")
        parameters.STEP24.get_value().set("STM M15")
        parameters.STEP25.get_value().set("STM M16")
        parameters.STEP26.get_value().set("INC M16")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.RO01, 2),
                (parameters.RO02, 3),
                (parameters.RO03, RealValue(RealValue(1 + 1 / 9).get() + RealValue(1 + 1 / 3).get()).get()),
                (parameters.M11, 9),
                (parameters.M12, 6),
                (parameters.M13, 5),
                (parameters.M14, 7),
                (parameters.M15, 10),
                (parameters.M16, 11),
            ],
        )

    def test_misc(self) -> None:
        parameters = CalcParameters()
        parameters.M01.get_value().set(1 + 1 / 9)
        parameters.M02.get_value().set(1 + 1 / 3)
        parameters.STEP01.get_value().set("IN -5")
        parameters.STEP02.get_value().set("ABS")
        parameters.STEP03.get_value().set("STM M01")

        execute_with_assertions(
            self,
            parameters,
            assertions=[(parameters.M01, 5)],
        )

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN -5")
        parameters.STEP02.get_value().set("CHS")
        parameters.STEP03.get_value().set("STM M01")
        parameters.STEP04.get_value().set("IN 5")
        parameters.STEP05.get_value().set("CHS")
        parameters.STEP06.get_value().set("STM M02")

        execute_with_assertions(
            self,
            parameters,
            assertions=[(parameters.M01, 5), (parameters.M02, -5)],
        )

        parameters = CalcParameters()
        parameters.M01.get_value().set(1 + 1 / 9)
        parameters.STEP01.get_value().set("IN M01")
        parameters.STEP02.get_value().set("RND")
        parameters.STEP03.get_value().set("STM M02")
        execute_with_assertions(self, parameters, assertions=[(parameters.M02, 1)])

        parameters = CalcParameters()
        parameters.M01.get_value().set(1 + 1 / 9)
        parameters.STEP01.get_value().set("IN M01")
        parameters.STEP02.get_value().set("TRC")
        parameters.STEP03.get_value().set("STM M02")
        execute_with_assertions(self, parameters, assertions=[(parameters.M02, 1)])

    def test_multiplicative(self) -> None:
        parameters = CalcParameters()
        parameters.M01.get_value().set(19.713)
        parameters.M02.get_value().set(5.9021)
        parameters.STEP01.get_value().set("IN M01")
        parameters.STEP02.get_value().set("IN M02")
        parameters.STEP03.get_value().set("IMOD")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("IN 10")
        parameters.STEP06.get_value().set("IN 2")
        parameters.STEP07.get_value().set("DIV")
        parameters.STEP08.get_value().set("STM M11")
        parameters.STEP09.get_value().set("IN 15")
        parameters.STEP10.get_value().set("DIV M11")
        parameters.STEP11.get_value().set("STM M12")
        parameters.STEP12.get_value().set("IN M01")
        parameters.STEP13.get_value().set("IN M02")
        parameters.STEP14.get_value().set("IDIV M14")
        parameters.STEP15.get_value().set("STM M13")
        parameters.STEP16.get_value().set("IN 10")
        parameters.STEP17.get_value().set("IN 2")
        parameters.STEP18.get_value().set("MUL")
        parameters.STEP19.get_value().set("STM M15")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.RO01, 4),
                (parameters.M11, 5),
                (parameters.M12, 3),
                (parameters.M13, 3),
                (parameters.M14, 4),
                (parameters.M15, 20),
            ],
        )

    def test_exponential(self) -> None:
        parameters = CalcParameters()
        parameters.M01.get_value().set(0.693147)
        parameters.M02.get_value().set(1.30103)
        parameters.M03.get_value().set(1.483)
        parameters.M04.get_value().set(3.1)
        parameters.STEP01.get_value().set("IN M01")
        parameters.STEP02.get_value().set("ALN")
        parameters.STEP03.get_value().set("OUT RO01")
        parameters.STEP04.get_value().set("IN M02")
        parameters.STEP05.get_value().set("ALOG")
        parameters.STEP06.get_value().set("OUT RO02")
        parameters.STEP07.get_value().set("IN M03")
        parameters.STEP08.get_value().set("EXP M04")
        parameters.STEP09.get_value().set("OUT RO03")
        parameters.STEP10.get_value().set("IN 1000")
        parameters.STEP11.get_value().set("LN")
        parameters.STEP12.get_value().set("STM M11")
        parameters.STEP13.get_value().set("IN 2000")
        parameters.STEP14.get_value().set("LOG")
        parameters.STEP15.get_value().set("STM M12")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.RO01, 2),
                (parameters.RO02, 19.984375),
                (parameters.RO03, 3.39453125),
                (parameters.M11, 6.90625),
                (parameters.M12, 3.30078125),
            ],
        )

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 4")
        parameters.STEP02.get_value().set("SQR")
        parameters.STEP03.get_value().set("STM M01")
        parameters.STEP04.get_value().set("SQRT")
        parameters.STEP05.get_value().set("STM M02")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.M01, 16),
                (parameters.M02, 4),
            ],
        )

    def test_statistics(self) -> None:
        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("IN 1")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("IN 5")
        parameters.STEP05.get_value().set("IN 10")
        parameters.STEP06.get_value().set("MEDN")
        parameters.STEP07.get_value().set("OUT RO01")

        execute_with_assertions(
            self,
            parameters,
            assertions=[(parameters.RO01, 2)],
        )

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("IN 1")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("IN 5")
        parameters.STEP05.get_value().set("IN 10")
        parameters.STEP06.get_value().set("MIN")
        parameters.STEP07.get_value().set("OUT RO01")
        parameters.STEP08.get_value().set("IN 1")
        parameters.STEP09.get_value().set("IN 1")
        parameters.STEP10.get_value().set("IN 2")
        parameters.STEP11.get_value().set("IN 5")
        parameters.STEP12.get_value().set("IN 10")
        parameters.STEP13.get_value().set("MAX")
        parameters.STEP14.get_value().set("OUT RO02")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.RO01, 1),
                (parameters.RO02, 10),
            ],
        )

        parameters = CalcParameters()
        parameters.M01.get_value().set(1 + 1 / 9)
        parameters.M02.get_value().set(1 + 1 / 3)
        parameters.STEP01.get_value().set("IN 4")
        parameters.STEP02.get_value().set("IN 2")
        parameters.STEP03.get_value().set("AVE")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("IN 4")
        parameters.STEP06.get_value().set("IN 5")
        parameters.STEP07.get_value().set("IN 10")
        parameters.STEP08.get_value().set("IN 15")
        parameters.STEP09.get_value().set("AVE 3")
        parameters.STEP10.get_value().set("OUT RO02")
        parameters.STEP11.get_value().set("IN M01")
        parameters.STEP12.get_value().set("AVE M02")
        parameters.STEP13.get_value().set("OUT RO03")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.RO01, 3),
                (parameters.RO02, 10),
                (parameters.RO03, RealValue((RealValue(1 + 1 / 9).get() + RealValue(1 + 1 / 3).get()) / 2).get()),
            ],
        )

    def test_trigonometry(self) -> None:
        parameters = CalcParameters()
        parameters.M01.get_value().set(0.841471)
        parameters.M02.get_value().set(1.557408)
        parameters.M03.get_value().set(0.5)
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("ACOS")
        parameters.STEP03.get_value().set("OUT RO01")
        parameters.STEP04.get_value().set("IN M01")
        parameters.STEP05.get_value().set("ASIN")
        parameters.STEP06.get_value().set("OUT RO02")
        parameters.STEP07.get_value().set("IN M02")
        parameters.STEP08.get_value().set("ATAN")
        parameters.STEP09.get_value().set("OUT RO03")
        parameters.STEP10.get_value().set("IN M03")
        parameters.STEP11.get_value().set("COS")
        parameters.STEP12.get_value().set("STM M11")
        parameters.STEP13.get_value().set("IN M03")
        parameters.STEP14.get_value().set("SIN")
        parameters.STEP15.get_value().set("STM M12")
        parameters.STEP16.get_value().set("IN M03")
        parameters.STEP17.get_value().set("TAN")
        parameters.STEP18.get_value().set("STM M13")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.RO01, 0),
                (parameters.RO02, 0.99951171875),
                (parameters.RO03, 1),
                (parameters.M11, 0.87744140625),
                (parameters.M12, 0.4794921875),
                (parameters.M13, 0.54638671875),
            ],
        )

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 10")
        parameters.STEP02.get_value().set("ACOS")
        parameters.STEP03.get_value().set("OUT RO01")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.PERROR, 3),
                (parameters.STERR, 2),
            ],
        )

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 10")
        parameters.STEP02.get_value().set("ASIN")
        parameters.STEP03.get_value().set("OUT RO01")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.PERROR, 2),
                (parameters.STERR, 2),
            ],
        )

    def test_rng(self) -> None:
        parameters = CalcParameters()
        parameters.M01.get_value().set(1000)
        parameters.M02.get_value().set(0.5)
        parameters.STEP01.get_value().set("RAND")
        parameters.STEP02.get_value().set("SUB M02")
        parameters.STEP03.get_value().set("ADD M03")
        parameters.STEP04.get_value().set("STM M03")
        parameters.STEP05.get_value().set("DEC M01")
        parameters.STEP06.get_value().set("IN M01")
        parameters.STEP07.get_value().set("BIP 1")

        execute_with_assertions(self, parameters, assertions=[])
        self.assertTrue(parameters.M03.get_value().get() != 0)
        self.assertTrue(parameters.M03.get_value().get() < 10)  # noqa: PLR2004
        self.assertTrue(parameters.M03.get_value().get() > -10)  # noqa: PLR2004

        parameters = CalcParameters()
        parameters.M01.get_value().set(1000)
        parameters.STEP01.get_value().set("RANG")
        parameters.STEP02.get_value().set("ADD M03")
        parameters.STEP03.get_value().set("STM M03")
        parameters.STEP04.get_value().set("DEC M01")
        parameters.STEP05.get_value().set("IN M01")
        parameters.STEP06.get_value().set("BIP 1")

        execute_with_assertions(self, parameters, assertions=[])
        self.assertTrue(parameters.M03.get_value().get() != 0)
        self.assertTrue(parameters.M03.get_value().get() < 10)  # noqa: PLR2004
        self.assertTrue(parameters.M03.get_value().get() > -10)  # noqa: PLR2004

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 100")
        parameters.STEP02.get_value().set("SEED")

        calc = execute_with_assertions(self, parameters, assertions=[])
        self.assertEqual(calc.seed, 100)

        parameters = CalcParameters()
        parameters.M01.get_value().set(200000)
        parameters.STEP01.get_value().set("IN M01")
        parameters.STEP02.get_value().set("SEED")
        parameters.STEP03.get_value().set("IN -1")
        parameters.STEP04.get_value().set("SEED")

        calc = execute_with_assertions(self, parameters, assertions=[])
        self.assertEqual(calc.seed, 100001)


class TestBoolean(unittest.TestCase):
    def test_basics(self) -> None:
        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("IN 1")
        parameters.STEP03.get_value().set("AND")
        parameters.STEP04.get_value().set("OUT BO01")
        parameters.STEP05.get_value().set("IN 0")
        parameters.STEP06.get_value().set("IN 1")
        parameters.STEP07.get_value().set("IN 1")
        parameters.STEP08.get_value().set("IN 1")
        parameters.STEP09.get_value().set("AND 3")
        parameters.STEP10.get_value().set("OUT BO02")
        parameters.STEP11.get_value().set("IN 0")
        parameters.STEP12.get_value().set("IN 1")
        parameters.STEP13.get_value().set("IN 1")
        parameters.STEP14.get_value().set("AND 3")
        parameters.STEP15.get_value().set("OUT BO03")
        parameters.STEP16.get_value().set("IN 1")
        parameters.STEP17.get_value().set("IN 0")
        parameters.STEP18.get_value().set("OR")
        parameters.STEP19.get_value().set("OUT BO04")
        parameters.STEP20.get_value().set("IN 1")
        parameters.STEP21.get_value().set("IN 0")
        parameters.STEP22.get_value().set("IN 0")
        parameters.STEP23.get_value().set("IN 0")
        parameters.STEP24.get_value().set("OR 3")
        parameters.STEP25.get_value().set("OUT BO05")
        parameters.STEP26.get_value().set("IN 1")
        parameters.STEP27.get_value().set("IN 1")
        parameters.STEP28.get_value().set("IN 1")
        parameters.STEP29.get_value().set("OR 3")
        parameters.STEP30.get_value().set("OUT BO06")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.BO01, True),
                (parameters.BO02, True),
                (parameters.BO03, False),
                (parameters.BO04, True),
                (parameters.BO05, False),
                (parameters.BO06, True),
            ],
        )


class TestProgramControl(unittest.TestCase):
    def test_termination(self) -> None:
        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("OUT RO01")
        parameters.STEP03.get_value().set("EXIT")
        parameters.STEP04.get_value().set("IN 2")
        parameters.STEP05.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 1)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("OUT RO01")
        parameters.STEP03.get_value().set("END")
        parameters.STEP04.get_value().set("IN 2")
        parameters.STEP05.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 1)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("OUT RO01")
        parameters.STEP03.get_value().set("BIT 5")
        parameters.STEP04.get_value().set("EXIT")
        parameters.STEP05.get_value().set("IN 2")
        parameters.STEP06.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 2)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("OUT RO01")
        parameters.STEP03.get_value().set("BIT 5")
        parameters.STEP04.get_value().set("END")
        parameters.STEP05.get_value().set("IN 2")
        parameters.STEP06.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 2)])

    def test_cond_branch(self) -> None:  # noqa: PLR0915
        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN -1")
        parameters.STEP02.get_value().set("BIN 6")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("EXIT")
        parameters.STEP06.get_value().set("IN 4")
        parameters.STEP07.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 4)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("BIN 6")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("EXIT")
        parameters.STEP06.get_value().set("IN 4")
        parameters.STEP07.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 2)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN -1")
        parameters.STEP02.get_value().set("BIP 6")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("EXIT")
        parameters.STEP06.get_value().set("IN 4")
        parameters.STEP07.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 2)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("BIP 6")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("EXIT")
        parameters.STEP06.get_value().set("IN 4")
        parameters.STEP07.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 4)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 0")
        parameters.STEP02.get_value().set("BIT 6")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("EXIT")
        parameters.STEP06.get_value().set("IN 4")
        parameters.STEP07.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 2)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("BIT 6")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("EXIT")
        parameters.STEP06.get_value().set("IN 4")
        parameters.STEP07.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 4)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 1")
        parameters.STEP02.get_value().set("BIF 6")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("EXIT")
        parameters.STEP06.get_value().set("IN 4")
        parameters.STEP07.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 2)])

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 0")
        parameters.STEP02.get_value().set("BIF 6")
        parameters.STEP03.get_value().set("IN 2")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("EXIT")
        parameters.STEP06.get_value().set("IN 4")
        parameters.STEP07.get_value().set("OUT RO01")
        execute_with_assertions(self, parameters, assertions=[(parameters.RO01, 4)])


class TestBasicRules(unittest.TestCase):
    def test_io(self) -> None:
        parameters = CalcParameters()
        parameters.BI01.get_value().set(True)
        parameters.RI01.get_value().set(123.456)
        parameters.HSCI1.get_value().set(200)
        parameters.HSCO1.get_value().set(200)
        parameters.II01.get_value().set(123)
        parameters.STEP01.get_value().set("IN BI01")
        parameters.STEP02.get_value().set("OUT BO01")
        parameters.STEP03.get_value().set("IN RI01")
        parameters.STEP04.get_value().set("OUT RO01")
        parameters.STEP05.get_value().set("OUT RO02")
        parameters.STEP06.get_value().set("IN II01")
        parameters.STEP07.get_value().set("OUT IO01")
        parameters.STEP10.get_value().set("IN")
        parameters.STEP11.get_value().set("OUT RO02")
        parameters.STEP12.get_value().set("IN ~BI01")
        parameters.STEP13.get_value().set("OUT BO02")
        parameters.STEP14.get_value().set("IN ~RI01")
        parameters.STEP15.get_value().set("OUT BO03")
        parameters.STEP16.get_value().set("IN 111")
        parameters.STEP17.get_value().set("STM M01")
        parameters.STEP18.get_value().set("END")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.BO01, True),
                (parameters.RO01, 123.4375),
                (parameters.IO01, 123),
                (parameters.RO02, 0),
                (parameters.BO02, False),
                (parameters.BO03, False),
                (parameters.M01, 111),
            ],
        )

    def test_memory(self) -> None:
        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 111")
        parameters.STEP02.get_value().set("STM M01")
        parameters.STEP03.get_value().set("STM M24")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.M01, 111),
                (parameters.M24, 111),
            ],
        )

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 111")
        parameters.STEP02.get_value().set("STM M01")
        parameters.STEP03.get_value().set("STM M24")
        parameters.STEP04.get_value().set("CLA")

        execute_with_assertions(
            self,
            parameters,
            assertions=[
                (parameters.M01, 0),
                (parameters.M24, 0),
            ],
        )

    def test_stack(self) -> None:
        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 111")
        calc = execute_with_assertions(self, parameters, assertions=[])
        self.assertEqual(len(calc.stack), 1)

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 111")
        parameters.STEP02.get_value().set("POP")
        calc = execute_with_assertions(self, parameters, assertions=[])
        self.assertEqual(len(calc.stack), 0)

    def test_comments(self) -> None:
        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN 111; IN 222")
        parameters.STEP02.get_value().set("STM M01 ;comment")
        execute_with_assertions(self, parameters, assertions=[(parameters.M01, 111)])

    def test_syntax_error(self) -> None:
        parameters = CalcParameters()
        parameters.STEP01.get_value().set("IN")
        parameters.STEP02.get_value().set("END")
        calc = execute_with_assertions(self, parameters, assertions=[])
        self.assertFalse(calc.syntax_error)

        parameters = CalcParameters()
        parameters.STEP01.get_value().set("TEST")
        calc = execute_with_assertions(self, parameters, assertions=[])
        self.assertTrue(calc.syntax_error)
