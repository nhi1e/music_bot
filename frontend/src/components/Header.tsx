import React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { SpotifyUser } from "@/types";

interface HeaderProps {
	user: SpotifyUser | null;
	onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ user, onLogout }) => {
	return (
		<div className="sticky top-0 z-50 bg-black">
			<div className="container mx-auto px-4 py-5 flex justify-between items-center">
				<h1 className="text-2xl pinyon-script-regular">Personal Music Bot</h1>
				<div className="flex items-center space-x-4">
					{user && (
						<div className="flex items-center space-x-3">
							<span className="text-sm adamina-regular">
								{user.display_name || user.id}
							</span>
							<DropdownMenu>
								<DropdownMenuTrigger>
									<Avatar className="h-8 w-8 border border-white/20">
										<AvatarImage
											src={
												user.images && user.images.length > 0
													? user.images[0].url
													: undefined
											}
											alt={user.display_name || user.id}
										/>
										<AvatarFallback className="bg-white/10 text-white text-xs adamina-regular">
											{(user.display_name || user.id).charAt(0).toUpperCase()}
										</AvatarFallback>
									</Avatar>
								</DropdownMenuTrigger>
								<DropdownMenuContent className="w-auto min-w-[6rem]">
									<DropdownMenuItem
										onClick={onLogout}
										className="cursor-pointer adamina-regular text-black hover:bg-white/10 focus:bg-white/10 px-2 py-2"
									>
										Logout
									</DropdownMenuItem>
								</DropdownMenuContent>
							</DropdownMenu>
						</div>
					)}
				</div>
			</div>
		</div>
	);
};
