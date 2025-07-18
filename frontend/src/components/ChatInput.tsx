import React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
	value: string;
	onChange: (value: string) => void;
	onSubmit: (e: React.FormEvent) => void;
	disabled: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
	value,
	onChange,
	onSubmit,
	disabled,
}) => {
	return (
		<div className="sticky adamina-regular bottom-0 left-0 w-full bg-black z-50">
			<form
				onSubmit={onSubmit}
				className="container mx-auto px-4 py-4 max-w-4xl flex space-x-2"
			>
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
					className="border-white text-black hover:shadow-[2px_2px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px] disabled:opacity-50"
					disabled={disabled || !value.trim()}
				>
					Send
				</Button>
			</form>
		</div>
	);
};
