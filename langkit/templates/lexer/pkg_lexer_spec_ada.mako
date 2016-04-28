## vim: filetype=makoada

with Ada.Containers;        use Ada.Containers;
with Ada.Containers.Hashed_Maps;
with Ada.Strings.Unbounded; use Ada.Strings.Unbounded;

with Interfaces; use Interfaces;

with Langkit_Support.Token_Data_Handler;
use Langkit_Support.Token_Data_Handler;

--  This package provides types and primitives to split text streams into lists
--  of tokens.

package ${_self.ada_api_settings.lib_name}.Lexer is

   Unknown_Charset : exception;
   --  Raised by Lex_From_* functions when the input charset is not supported

   Invalid_Input : exception;
   --  Raised by Lex_From_* functions when the input contains an invalid byte
   --  sequence.

   procedure Lex_From_Filename (Filename, Charset : String;
                                TDH               : in out Token_Data_Handler;
                                With_Trivia       : Boolean);
   --  Extract tokens out of Filename and store them into TDH. Raise a
   --  Name_Error exception if the file could not be open.

   procedure Lex_From_Buffer (Buffer, Charset : String;
                              TDH             : in out Token_Data_Handler;
                              With_Trivia     : Boolean);
   --  Likewise, but extract tokens from an in-memory buffer. This never raises
   --  an exception.

   function Token_Text (Token_Id : Unsigned_16) return String;
   --  Return a human-readable name for some token kind

   ## When generated code needs to deal with token kinds, it could use integer
   ## literals but this would not be convenient to read. Generate named
   ## constants for each token kind instead.

   % for tok in sorted(get_context().lexer.tokens_class, \
                       key=lambda tok: tok.value):
       ${get_context().lexer.c_token_name(tok)} : constant := ${tok.value};
   % endfor

private

   function Hash (N : Unsigned_16) return Ada.Containers.Hash_Type is
     (Ada.Containers.Hash_Type (N));

   package Token_Text_Maps is new Ada.Containers.Hashed_Maps
     (Key_Type        => Unsigned_16,
      Element_Type    => Unbounded_String,
      Hash            => Hash,
      Equivalent_Keys => "=");

   Token_Text_Map : Token_Text_Maps.Map;

   function Token_Text (Token_Id : Unsigned_16) return String is
     (To_String (Token_Text_Map.Element (Token_Id)));

end ${_self.ada_api_settings.lib_name}.Lexer;
