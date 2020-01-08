import string

# (1, 4, 5)
# use {plural|...} to skip 1 number and {plural1|...} to keep it, 
# use {plural0|...} to not display numbers
class PluralFormatter(string.Formatter):
    def output(self, value, label, format_spec):
        if format_spec.startswith('plural0|') or (format_spec.startswith('plural|') and value == 1):
            return '{}'.format(label)
        else:
            return '{} {}'.format(value, label)

    def format_field(self, value, format_spec):
        if format_spec.startswith('plural'):
            words = format_spec.split('|')
            num = value % 100;
            if num >= 11 and num <= 19:
                return self.output(value, words[3], format_spec)
            else:
                i = num % 10
                if i == 1:
                    return self.output(value, words[1], format_spec)
                elif i in [2,3,4]:
                    return self.output(value, words[2], format_spec)
                else:
                    return self.output(value, words[3], format_spec)
        else:
            return super().format_field(value, format_spec)

fmt = PluralFormatter()
