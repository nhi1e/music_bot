import React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
	value: string;
	onChange: (value: string) => void;
	onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
	disabled?: boolean;
}

const speakerLeft = `
#########\\
#(=====)# |
######### |
#-------# |
#|  -  |# |          --
#|( O )|# |    --  --  
#|  -  |# |  --  --  
#|-----|# | --       
#########/`;

// Mirrored speaker using string manipulation
const speakerRight = `
             /#########
            | #(=====)#
            | #########
            | #-------#
--          | #|  -  |#
  --  --    | #|( O )|#
    --  --  | #|  -  |#
		 --	| #|-----|#
			 \\#########`;
export const ChatInput: React.FC<ChatInputProps> = ({
	value,
	onChange,
	onSubmit,
	disabled,
}) => {
	return (
		<div className="sticky bottom-0 w-full bg-black z-50 p-4 flex justify-center items-start">
			{/* Left speaker */}
			<pre className="text-white font-mono text-xs leading-[10px] select-none">
				{speakerLeft}
			</pre>

			{/* Input and button - exactly chat width */}
			<div className="w-full max-w-4xl flex items-start">
				<form onSubmit={onSubmit} className="flex flex-1 items-start">
					<Input
						type="text"
						placeholder="Ask about music, playlists, or get recommendations..."
						value={value}
						onChange={(e) => onChange(e.target.value)}
						className="flex-1 bg-black border-white text-white placeholder:text-white/50 focus:border-white focus:ring-white/50"
						disabled={disabled}
					/>
					<Button
						type="submit"
						variant="outline"
						className="ml-2 border-white text-black hover:shadow-[2px_2px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px] disabled:opacity-50"
						disabled={disabled || !value.trim()}
					>
						Send
					</Button>
				</form>
			</div>

			{/* Right speaker */}
			<pre className="text-white font-mono text-xs leading-[10px] select-none">
				{speakerRight}
			</pre>
		</div>
	);
};
