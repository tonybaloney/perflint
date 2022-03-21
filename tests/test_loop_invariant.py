import astroid
import perflint.for_loop_checker
from base import BaseCheckerTestCase


class TestUniqueReturnChecker(BaseCheckerTestCase):
    CHECKER_CLASS = perflint.for_loop_checker.LoopInvariantChecker

    def test_basic_loop_invariant(self):
        test_node = astroid.extract_node("""
        def test(): #@
            items = (1,2,3,4)

            for item in list(items):
                x = print("There are ", len(items), "items")
        """)

        with self.assertAddedMessage("loop-invariant-statement"):
            self.walk(test_node)

    def test_basic_loop_invariant_while(self):
        test_node = astroid.extract_node("""
        def test(): #@
            items = (1,2,3,4)
            i = 0
            while i < len(items):
                x = print("There are ", len(items), "items")
                i += 1
        """)

        with self.assertAddedMessage("loop-invariant-statement"):
            self.walk(test_node)

    def test_basic_loop_variant_while(self):
        test_node = astroid.extract_node("""
        def test(): #@
            items = (1,2,3,4)
            i = 0
            while i < len(items):
                i += 1
                print(i)
        """)

        with self.assertAddedMessage("loop-invariant-statement"):
            self.walk(test_node)

    def test_kwarg_usage_in_while(self):
        test_node = astroid.extract_node("""
        def foo(arg):
            pass

        def test(): #@
            items = (1,2,3,4)
            i = 0
            while i < len(items):
                foo(arg=i)
        """)

        with self.assertNoMessages():
            self.walk(test_node)

    def test_basic_loop_variant_by_method(self):
        test_node = astroid.extract_node("""
        def test(): #@
            items = [1,2,3,4]

            for item in items:
                x = print("There are ", len(items), "items")
                items.clear()
        """)

        with self.assertNoMessages():
            self.walk(test_node)

    def test_global_in_for_loop(self):
        test_func = astroid.extract_node("""
        glbl = 1

        def test(): #@
            items = (1,2,3,4)

            for item in list(items):
                glbl
        """)

        with self.assertAddedMessage("loop-invariant-global-usage"):
            self.walk(test_func)

    def test_assigned_global_in_for_loop(self):
        test_func = astroid.extract_node("""
        glbl = 1

        def test(): #@
            items = (1,2,3,4)

            for glbl in list(items):
                glbl
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_self_assignment_for_loop(self):
        test_func = astroid.extract_node("""
        class Foo:
            n = 1

            def loop(self):
                for self.n in range(4):
                    print(self.n)
        
        def test(): #@
            f = Foo()
            f.loop()
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_byte_slice(self):
        test_func = astroid.extract_node("""
        def test(): #@
            word = b'word'

            for i in range(10):
                word[0:i]
        """)

        with self.assertAddedMessage("memoryview-over-bytes"):
            self.walk(test_func)
    
    def test_byte_slice_as_arg(self):
        test_func = astroid.extract_node("""
        def test(arg1: bytes): #@
            for i in range(10):
                arg1[0:i]
        """)

        with self.assertAddedMessage("memoryview-over-bytes"):
            self.walk(test_func)
        
    def test_dotted_name_in_loop(self):
        test_func = astroid.extract_node("""
        import os
        def test(): #@
            for item in items:
                os.environ[item]
        """)

        with self.assertAddedMessage("dotted-import-in-loop"):
            self.walk(test_func)

    def test_worse_dotted_name_in_loop(self):
        test_func = astroid.extract_node("""
        import os
        def test(): #@
            for item in items:
                os.path.exists(item)
        """)

        with self.assertAddedMessage("dotted-import-in-loop"):
            self.walk(test_func)

    def test_variant_f_string_in_loop(self):
        test_func = astroid.extract_node("""
        def test(): #@
            n = 0
            for i in range(2):
                print(f"{n} {i}")
        """)

        with self.assertNoMessages():
            self.walk(test_func)

    def test_invariant_f_string_in_loop(self):
        test_func = astroid.extract_node("""
        def test(): #@
            i = 2
            for _ in range(2):
                print(f"{i}")
        """)

        with self.assertAddedMessage("loop-invariant-statement"):
            self.walk(test_func)

    def test_call_side_effect(self):
        test_func = astroid.extract_node("""
        class Foo:
            pass

        def test(): #@
            for n in range(1):
                Foo()
        """)

        with self.assertNoMessages():
            self.walk(test_func)
    
    def test_assign_const(self):
        test_func = astroid.extract_node("""
        def test(): #@
            for n in range(1):
                x = None
        """)

        with self.assertNoMessages():
            self.walk(test_func)
    
    def test_slice_fragment(self):
        test_func = astroid.extract_node("""
        def test(): #@
            for n in range(1):
                x = None
        """)

        with self.assertNoMessages():
            self.walk(test_func)
    
    def test_index_fragment(self):
        test_func = astroid.extract_node("""
        def test(): #@
            fruits = ["apple", "banana", "pear"]
            for fruit in fruits:
                print(fruit)
                _ = fruit[1:]
                _ = fruit[-1]
                _ = fruit[::-1] 
        """)

        with self.assertNoMessages():
            self.walk(test_func)
    

    def test_return(self):
        test_func = astroid.extract_node("""
        def test(): #@
            fruits = ["apple", "banana", "pear"]
            for _ in fruits:
                return fruits
        """)

        with self.assertNoMessages():
            self.walk(test_func)
    