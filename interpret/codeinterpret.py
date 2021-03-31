
import errors
import variable as v

class CodeInterpret(object):
    """
    Trieda vykonávajúca interpretáciu kódu.

    Instančné atribúty:
        instructions (dict): order => (kód, [argumenty])
        label_dict (dict): návestie => index v instructions
        gf (frame): globálny rámec
        tf (frame): dočasný rámec, pôvodne None
        lf_stack (list): zásobník lokálnych rámcov
        current_instr (str): meno aktuálne spracovávanej inštrukcie
        current_args (dict): argumenty aktuálne spracovávanej inštrukcie, pozícia => argument
        counter (list): čítač inštrukcií

    Metody:
        - Obsahuje metodu pre každú inštrukciu IPPcode21, ktoré modifikujú stav
          objektu.

    """

    def __init__(self):
        """
        Konštruktor.
        """
        self.instructions = dict()
        self.label_dict = dict()
        self.gf = Frame()
        self.tf = None
        self.lf_stack = list()
        self.current_instr = ""
        self.current_args = dict()
        self.counter = 0

    def newInstruction(self, name):
        """
        Začne spracovávať novú inštrukciu. Vymazanie obsahu zoznamu current_args a prepísanie mena v current_instr.

        Parametre:
            name (str): názov inštrukcie (operačný kód)
        """

        self.current_instr = name
        self.current_args = dict()

    def addArgument(self, value, num):
        """
        Pridanie value na poziciu index num - 1 zoznamu current_args. Predpokladá spravný hodnotu a nevykonáva kontrolu.

        Parametre:
            value (tuple): hodnota argumentu v tvare (typ, hodnota)
            num (int): číslo argumentu
        """

        self.current_args[num] = value

    def finishInstruction(self, order):
        """
        Pridanie aktuálne spracovávanej inštrukcie na pozíciu order - 1 v zozname instructions.

        Parametre:
            order (int): poradie inštrukcie
        """

        args = [self.current_args[key] for key in sorted(self.current_args.keys())]

        if self.current_instr == "LABEL":
            self.addLabel(*args, order)
        
        if order in self.instructions.keys():
            errors.error(f"Opakované zadanie inštrukcie s číslom {order}.", errors.XML_STRUCT)

        self.instructions[order] = (self.current_instr, args)
        self.current_args = dict()
    
    def run(self):
        """
        Prechádza zoznamom inštrukcií instructions a volá odpovedajúce metody s danými parametrami
        """
        
        num_instr = len(self.instructions)
        keys_sorted = sorted(self.instructions.keys())


        for index, instr in self.instructions.items():
            print(index, instr)

        print("------------------------------")

        while self.counter < num_instr:
            instruction = (self.instructions[keys_sorted[self.counter]])
            print(self.counter, instruction[0], instruction[1])
            getattr(self, instruction[0])(*instruction[1])

            for key, val in self.gf.vars.items():
                print(key + " => " + str(val))

            print("------------------------------")

            self.counter += 1

    def addLabel(self, name, line):
        """
        Pridanie návestia do labels_dict. Bude vykonaný skok na pozíciu
        v instructions, kde sa nachádza návestie. V záp

        Parametre:
            name (tuple): názov návestia (label, meno)
            line (int): číslo riadku (order - 1)
        """

        if name[1] in self.label_dict:
            errors.error(f"Opakovaná definícia návestia '{name[1]}'.", errors.SEMANTIC)

        self.label_dict[name[1]] = line - 1

    def parseName(self, name):
        """
        Z názvu premennej odvodí rámec a skontroluje dostupnosť.

        Parametre:
            name (string): názov premennej vo formáte ramec@meno
        
        Výstup:
            (Name, Frame): meno premmenej, rámec premennej
        """

        parts = name.partition("@")
        frame_str = parts[0]
        name = parts[-1]
        
        if frame_str == "GF":
            frame = self.gf
        elif frame_str == "TF":
            if self.tf is None:
                errors.error("Dočasný rámec neexistuje.", errors.NO_FRAME)
            
            frame = self.tf
        elif frame_str == "LF":
            if not self.lf_stack:
                errors.error("Lokálny rámec neexistuje.", errors.NO_FRAME)

            frame = self.lf_stack[-1]

        return (name, frame)
    
    def getVariable(self, var):
        """
        Získa objektu typu Variable reprezentujúci premennú alebo konštantu..
        
        Parametre:
            var (tuple): premenná alebo konštanta (typ, hodnota)
        
        Výstup:
            Variable: premenná alebo konštanta
        """
    
        if var[0] == "var":
            name, frame = self.parseName(var[1])
            return frame.getVariable(name)
        else:
            return v.Variable.fromDefinition(*var)


    def DEFVAR(self, var):
        """
        Vytvorenie novej premennej v danom rámci.
        
        Parametre:
            var (tuple): názov premennej vo formáte (typ, ramec@meno)
        """
        
        name, frame = self.parseName(var[1])
       
        frame.defVariable(name)

    def MOVE(self, var, symb):
        """
        Uloženie hodnoty symb do premennej var

        Parametre:
            var (string): názov premennej vo formáte (typ, ramec@meno)
            symb (tuple): hodnota vo formáte (typ, hodnota)
        """
        name, frame = self.parseName(var[1])
        
        frame.getVariable(name).setValue(*symb)
            

    def LABEL(self, label):
        """
        Nič sa nevykoná. Návestia sú zaznamenané už pri náčítaní kódu.
        Metóda bola implementovaná kvôli konzistencii spôsobu vykonávania inštrukcií.

        Parametre:
            label (tuple): meno návestia (label, meno)
        """
        
        pass

    def JUMP(self, label):
        """
        Bude vykonaný skok na pozíciu v instructions, kde sa nachádza návestie label..

        Parametre:
            label (tuple): názov návestia (label, meno)
        """

        if label[1] not in self.label_dict:
            errors.error(f"Skok na nedefinované návestie '{label[1]}'.", errors.SEMANTIC)

        self.counter = self.label_dict[label[1]] 

    def JUMPIFEQ(self, label, symb1, symb2):
        """
        Inštrukcia podmieneného skoku.

        Parametre:
            label (tuple): názov návestia (label, meno)
            symb1 (tuple): argument (typ, hodnota)
            symb2 (tuple): argument (typ, hodnota)
        """
    
        var1 = self.getVariable(symb1)
        var2 = self.getVariable(symb2)

        if var1.isNil() or var2.isNil():
            self.jump(label)
        
        if var1 == var2:
            self.jump(label)
    
    def JUMPIFNEQ(self, label, symb1, symb2):
        """
        Inštrukcia podmieneného skoku.

        Parametre:
            label (tuple): názov návestia (label, meno)
            symb1 (tuple): argument (typ, hodnota)
            symb2 (tuple): argument (typ, hodnota)
        """

        var1 = self.getVariable(symb1)
        var2 = self.getVariable(symb2)

        if var1.isNil() or var2.isNil():
            self.jump(label)
        
        if var1 != var2:
            self.jump(label)

    def READ(self, var, typ):
        """
        Inštrukcia pre čítanie vstupu.

        Parametre:
            var (tuple): premenná (var, meno)
            typ (tuple): typ vstupu (type, typ)
        """

        act_type = typ[1]
        data = ""

        try:
            data = input()
        except EOFError:
            data = "nil"
            act_type = "nil"

        if typ[1] == "int":
            try:
                int(data)
            except ValueError:
                data = "nil"
                act_type = "nil"
        elif typ[1] == "bool":
            data = "true" if data.lower() == "true" else "false"

        self.getVariable(var).setValue(act_type, data)

    def WRITE(self, symb):
        """
        Inštrukcie pre výpis obsahu premennej alebo konštanty.

        Parametre:
            symb (tuple): premenná alebo konštanta (typ, hodnota)
        """

        var = self.getVariable(symb)

        if var.isNil():
            print("", end = "")
        if var.isBool():
            if var.getValue() == True:
                print("true", end = "")
            else:
                print("false", end = "")
        else:
            print(var.getValue())

    def CONCAT(self, var, symb1, symb2):
        """
        Inštrukcia konkatenácie.
        Do var je uložená konkatenácia reťazcov symb1 a symb2.

        Parametre:
            var (tuple): premenná (typ, meno)
            symb1 (tuple): prvý reťazec ('string', hodnota)
            symb2 (tuple): druhý reťazec ('string', hodnota)
        """
        
        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)

        if not symb1_o.isString() or not symb2_o.isString():
            errors.error(f"Nepodporované hodnoty typov v inštrukcii concat.", errors.OP_TYPES)

        res = symb1_o.getValue() + symb2_o.getValue()

        var_o.setValue("string", res)

    def ADD(self, var, symb1, symb2):
        """
        Sčíta symb1 a symb2, výsledok uloží do var.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): celočíselná premenná alebo konštanta (int, hodnota)
            symb2 (tuple): celočíselná premenná alebo konštanta (int, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)
       
        res = symb1_o + symb2_o

        var_o.setValue("int", res.getValue())

    def SUB(self, var, symb1, symb2):
        """
        Odčíta symb1 a symb2, výsledok uloží do var.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): celočíselná premenná alebo konštanta (int, hodnota)
            symb2 (tuple): celočíselná premenná alebo konštanta (int, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)
       
        res = symb1_o - symb2_o

        var_o.setValue("int", res.getValue())

    def MUL(self, var, symb1, symb2):
        """
        Vynásobí symb1 a symb2, výsledok uloží do var.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): celočíselná premenná alebo konštanta (int, hodnota)
            symb2 (tuple): celočíselná premenná alebo konštanta (int, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)
       
        res = symb1_o * symb2_o

        var_o.setValue("int", res.getValue())

    def IDIV(self, var, symb1, symb2):
        """
        Podelí symb1 symb2, výsledok uloží do var.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): celočíselná premenná alebo konštanta (int, hodnota)
            symb2 (tuple): celočíselná premenná alebo konštanta (int, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)
       
        res = symb1_o // symb2_o

        var_o.setValue("int", res.getValue())

    def LT(self, var, symb1, symb2):
        """
        Porovná symb1 a symb2, výsledok uloží do var.
        Symb1 a symb2 musia byť rovnakého typu.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): premenná alebo konštanta (typ, hodnota)
            symb2 (tuple): premenná alebo konštanta (typ, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)
        
        res = symb1_o < symb2_o
            
        if res:
            var_o.setValue("bool", "true")
        else:
            var_o.setValue("bool", "false")
    
    def GT(self, var, symb1, symb2):
        """
        Porovná symb1 a symb2, výsledok uloží do var.
        Symb1 a symb2 musia byť rovnakého typu.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): premenná alebo konštanta (typ, hodnota)
            symb2 (tuple): premenná alebo konštanta (typ, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)
        
        res = symb1_o > symb2_o
            
        if res:
            var_o.setValue("bool", "true")
        else:
            var_o.setValue("bool", "false")
    
    def EQ(self, var, symb1, symb2):
        """
        Porovná symb1 a symb2, výsledok uloží do var.
        Symb1 a symb2 musia byť rovnakého typu.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): premenná alebo konštanta (typ, hodnota)
            symb2 (tuple): premenná alebo konštanta (typ, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)
        
        res = symb1_o == symb2_o
            
        if res:
            var_o.setValue("bool", "true")
        else:
            var_o.setValue("bool", "false")

    def AND(self, var, symb1, symb2):
        """
        Vykoná logický 'and' nad symb1 a symb2, výsledok uloží do var.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): booleovská premenná alebo konštanta (bool, hodnota)
            symb2 (tuple): booleovské premenná alebo konštanta (bool, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)
        
        res = symb1_o & symb2_o

        if res:
            var_o.setValue("bool", "true")
        else:
            var_o.setValue("bool", "false")

    def OR(self, var, symb1, symb2):
        """
        Vykoná logický 'or' nad symb1 a symb2, výsledok uloží do var.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): booleovská premenná alebo konštanta (bool, hodnota)
            symb2 (tuple): booleovská premenná alebo konštanta (bool, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        symb2_o = self.getVariable(symb2)
        
        res = symb1_o | symb2_o

        if res:
            var_o.setValue("bool", "true")
        else:
            var_o.setValue("bool", "false")

    def NOT(self, var, symb1):
        """
        Vykoná logickú negáciu symb1..

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb1 (tuple): booleovská premenná alebo konštanta (bool, hodnota)
        """

        var_o = self.getVariable(var)
        symb1_o = self.getVariable(symb1)
        
        res = ~ symb1_o

        if res:
            var_o.setValue("bool", "true")
        else:
            var_o.setValue("bool", "false")
        
    def INT2CHAR(self, var, symb):
        """
        Prevod celého čísla symb na znak, podla kódovania Unicode.

        Parametre:
            var (tuple): premenná (var, hodnota)
            symb (tuple): celočíselná premenná alebo konštanta (typ, hodnota)
        """

        var_o = self.getVariable(var)
        symb_o = self.getVariable(symb)
        
        
        if not symb_o.isInt():
            errors.error("Chybný typ operandu v inštrukcii INT2CHAR.", errors.OP_TYPE)

        try:
            char = chr(symb_o.getValue())
            var_o.setValue("string", char)
        except ValueError:
            errors.error(f"Hodnotu {symb_o.getValue()} nie je možné konvertovať na znak v inštrukcii INT2CHAR.", errors.BAD_STRING)

class Frame(object):
    """
    Objekt reprezentujúci pamäťový rámec.

    Instančné atribúty:
        vars (dict): meno premennej => premmenná (Variable)

    Metódy:
        defVariable(self, name): definícia premennej
        setValue(self, name, value): nastavenie novej hodnoty premennej
        getValeu(self, name): získanie hodnoty premennej
        isDef(self, name): overenie definície premennej
        getType(self, name): získanie typu premennej
    """

    def __init__(self):
        """
        Konštruktor.
        """

        self.vars = dict()

    def defVariable(self, name):
        """
        Definícia premennej.

        Parametre:
            name (string): meno premennej
        """
        
        if self.isDef(name):
            errors.error(f"Opakovaná definícia premennej '{name}'.", errors.SEMANTIC)

        self.vars[name] = v.Variable.fromDeclaration()

    def getVariable(self, name):
        """
        Získanie objektu reprecentujúceho premennú..

        Parametre:
            name (string): meno premennej
        
        Výstup:
            Variable: premenná
        """

        if not self.isDef(name):
            errors.error(f"Nedefinovaná premenná '{name}'.", errors.UNDEF_VAR)
        
        return self.vars[name]

    
    def isDef(self, name):
        """
        Overí, či daná premenná je definovaná.

        Parametre:
            name (string): meno premennej

        Výstup:
            bool: True ak premenná je definovaná, inak False

        """

        return name in self.vars
