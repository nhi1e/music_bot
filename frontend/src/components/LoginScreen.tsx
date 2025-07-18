import React from "react";
import { asciiBackground } from "@/assets/ascii_art";

interface LoginScreenProps {
	onSpotifyLogin: () => void;
}

export const LoginScreen: React.FC<LoginScreenProps> = ({ onSpotifyLogin }) => {
	return (
		<div className="relative min-h-screen bg-black flex items-center justify-center px-4 overflow-hidden">
			<pre className="absolute inset-0 text-white text-[20px] leading-none pointer-events-none z-0 select-none p-2 whitespace-pre-wrap">
				{asciiBackground}
			</pre>
			<div className="w-full max-w-sm text-white text-center space-y-6">
				<h1 className="text-7xl pinyon-script-regular">Personal Music Bot</h1>
				<button
					onClick={onSpotifyLogin}
					className="w-full bg-black border border-white text-white adamina-regular font-semibold py-4 px-6 transition-all duration-200 transform flex items-center justify-center space-x-3 hover:shadow-[4px_4px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px]"
				>
					Continue with Spotify
				</button>
			</div>
		</div>
	);
};
