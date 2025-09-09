import sys

from crossword import *
import itertools
import copy


class CrosswordCreator():                                                       # use to solve the crossword puzzle.

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):                                          # letter_grid is a helper function used by both print and save that generates a 2D list of all characters in their appropriate positions for a given assignment.
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):                                                # will print to the terminal a representation of your crossword puzzle for a given assignment
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):                                       # save, meanwhile, will generate an image file corresponding to a given assignment.
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):                                                            # solve function. This function does three things:
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()                                         # first, it calls enforce_node_consistency to enforce node consistency on the crossword puzzle, ensuring that every value in a variable’s domain satisfy the unary constraints. 
        self.ac3()                                                              #  Next, the function calls ac3 to enforce arc consistency, ensuring that binary constraints are satisfied.
        return self.backtrack(dict())                                           # Finally, the function calls backtrack on an initially empty assignment (the empty dictionary dict()) to try to calculate a solution to the problem.

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):                                                     # The revise function should make the variable x arc consistent with the variable y.
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """                                                                     # Recall that x is arc consistent with y when every value in the domain of x has a possible value in the domain of y that does not cause a conflict.
        words_to_remove = []                                                    # To make x arc consistent with y, you’ll want to remove any value from the domain of x that does not have a corresponding possible value in the domain of y.

        overlap = self.crossword.overlaps[x, y]                                 # Recall that you can access self.crossword.overlaps to get the overlap, if any, between two variables. The domain of y should be left unmodified.                          

        if overlap is None:
            return False
        else:
            a, b = overlap
        # a and b are positions of overlap, wrt vars x and y
        for word1 in self.domains[x]:
            overlap_possible = False
            for word2 in self.domains[y]:
                if word1 != word2 and word1[a] == word2[b]:
                    overlap_possible = True
                    break
            if not overlap_possible:
                words_to_remove.append(word1)
            
        for word in words_to_remove:
            self.domains[x].remove(word)
        return len(words_to_remove) > 0                                         # The function should return True if a revision was made to the domain of x; it should return False if no revision was made.

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:                                                        # If `arcs` is None, build a queue of all arcs (X, Y) where X and Y are variables with a constraint between them.
            queue = list(itertools.product(self.crossword.variables, self.crossword.variables))
            queue = [arc for arc in queue if arc[0] != arc[1] and self.crossword.overlaps[arc[0], arc[1]] is not None]
        else:
            queue = arcs                                                        # If arcs argument is given → start with that list of arcs.

        while queue:                                                            # While the queue is not empty:
            arc = queue.pop(0)                                                  # Dequeue (X, Y).
            x, y = arc[0], arc[1] 

            if self.revise(x, y):                                               # Call revise(X, Y). This will remove values from X’s domain if they have no support in Y’s domain.
                if not self.domains[x]:                                         # If no values are left in X → ❌ impossible problem, return False.
                    print("ending ac3")
                    return False
                
                for z in (self.crossword.neighbors(x) - {y}):                   # If revise changed X’s domain. Then we need to recheck all neighbors of X (except Y, since we just checked it).
                    queue.append((z, x))                                        # So for each neighbor Z of X (Z ≠ Y), enqueue (Z, X).
        return True

    def assignment_complete(self, assignment):                                  # check to see if a given assignment is complete.
        """                                                                     # An assignment is a dictionary where the keys are Variable objects and the values are strings representing the words those variables will take on.
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if set(assignment.keys()) == self.crossword.variables and all(assignment.values()): # An assignment is complete if every crossword variable is assigned to a value (regardless of what that value is).
            return True                                                         # The function should return True if the assignment is complete and return False otherwise.
        else:
            return False

    def consistent(self, assignment):                                           #  function should check to see if a given assignment is consistent.
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # An assignment is consistent if it satisfies all of the constraints of the problem: that is to say, all values are distinct, every value is the correct length, and there are no conflicts between neighboring variables.
        for variable1 in assignment:
            word1 = assignment[variable1]
            if variable1.length != len(word1):
                # word length doesn't satisfy constraints
                return False

            for variable2 in assignment:
                word2 = assignment[variable2]
                if variable1 != variable2:
                    if word1 == word2:
                        # two variables mapped to the same word
                        return False

                    overlap = self.crossword.overlaps[variable1, variable2]
                    if overlap is not None:
                        a, b = overlap
                        if word1[a] != word2[b]:
                            # words don't satisfy overlap constraints
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        return self.domains[var]

    def select_unassigned_variable(self, assignment):                           
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):                                # If all crossword slots are filled consistently, we’ve solved the puzzle → return the solution.
            return assignment

        var = self.select_unassigned_variable(assignment)                       # Pick a slot (variable) that doesn’t have a word yet. Usually chosen with heuristics (like MRV = Minimum Remaining Values: pick the slot with fewest possible words).
        for value in self.order_domain_values(var, assignment):                 # Try assigning a word (value) from the possible words in var’s domain.
            test_assignment = copy.deepcopy(assignment)
            test_assignment[var] = value                                        # Temporarily assign the word to the slot.
            if self.consistent(test_assignment):                                # Check if this partial assignment is still consistent
                assignment[var] = value
                result = self.backtrack(assignment)                             # If consistent → recurse with this new assignment.
                if result is not None:                                          # If recursion finds a full solution, return it upward.
                    return result
            assignment.pop(var, None)                                           # If recursion fails (dead end), undo the assignment (backtrack) and try another word.
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
