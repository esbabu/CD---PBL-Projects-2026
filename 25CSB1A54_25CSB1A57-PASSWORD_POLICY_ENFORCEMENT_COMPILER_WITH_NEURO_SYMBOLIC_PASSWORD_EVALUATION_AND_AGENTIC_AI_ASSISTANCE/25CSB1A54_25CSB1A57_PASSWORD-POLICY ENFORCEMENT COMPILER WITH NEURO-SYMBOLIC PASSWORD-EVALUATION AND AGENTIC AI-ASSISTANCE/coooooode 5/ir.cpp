#include "ir.h"

PolicyIR buildIR(const PolicyConstraints& c)
{
    PolicyIR ir;

    ir.minLength = c.minLength;
    ir.maxLength = c.maxLength;

    ir.requireUpper = (c.requireUpper == 1);
    ir.requireLower = (c.requireLower == 1);
    ir.requireDigit = (c.requireDigit == 1);
    ir.requireSpecial = (c.requireSpecial == 1);
    ir.noSpaces = (c.noSpaces == 1);

    return ir;
}
