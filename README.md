# CS50's AI Crossword Project

Create an AI that generates complete crossword puzzles using constraint satisfaction techniques such as node consistency, arc consistency (AC-3), and backtracking search, enhanced by heuristics.

**Problem Definition**
  * Input:
    * A crossword structure file (structureX.txt) that defines which grid cells should be filled (using _ for blanks).
    * A words list (wordsX.txt) serving as the vocabulary of possible words.
  * Goal:
    * Place a unique word from the vocabulary into each across and down entry such that:
      * Each word fits the specified length (unary constraint).
      * Overlapping letters between across/down entries match (binary constraints).
      * No word is used more than once in the entire puzzle.

**Core Model: Constraint Satisfaction Problem (CSP)**

  * Variables: Each sequence of blank squares (an across or down slot).
    * Defined by i, j coordinates, direction (ACROSS / DOWN), and length. 
  * Domains: Initially, every variable's domain is the full vocabulary.
  * Constraints:
    * Unary: Word length must equal variable length → filtered via node consistency.
    * Binary: Overlapping entries must share the same letter at the overlap position.
    * All-different: Enforce that all filled words are distinct
   
**Architecture & Provided Files**
  * crossword.py:
    * Defines classes:
      * Variable: Encapsulates an entry's position, direction, and length.
      * Crossword: Manages puzzle dimensions, blank layout, variables, vocabulary, and overlaps between variables; also provides neighbor lookups. 
  * generate.py:
    * Contains CrosswordCreator class to solve the puzzle:
      * self.domains: Maps variables → set of possible words.
      * Utility methods:
        * print: Show the current assignment in the terminal.
        * save: Save a visual representation (requires Pillow library).
      * Key functions to implement:
        * enforce_node_consistency
        * revise
        * ac3
        * assignment_complete
        * consistent
        * order_domain_values
        * select_unassigned_variable
        * backtrack 
