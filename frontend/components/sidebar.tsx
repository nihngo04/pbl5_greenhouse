"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, LineChart, Brain, Settings, ChevronLeft, ChevronRight, Sprout, Activity } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { useMemo, useState } from "react"

const sidebarItems = [
	{
		title: "Dashboard",
		href: "/dashboard",
		icon: LayoutDashboard,
	},
	{
		title: "Trực Quan Dữ Liệu",
		href: "/visualization",
		icon: LineChart,
	},
	{
		title: "Nhận Diện Sâu Bệnh",
		href: "/disease-detection",
		icon: Brain,
	},
	{
		title: "Quản Lý Thông Tin",
		href: "/management",
		icon: Settings,
	},
	{
		title: "System Monitoring",
		href: "/monitoring",
		icon: Activity,
	},
]

export function Sidebar() {
	const pathname = usePathname()
	const [collapsed, setCollapsed] = useState(false)
	const mounted = useMemo(() => true, [])

	return (
		<motion.aside
			initial={false}
			animate={{
				width: collapsed ? 80 : 256,
			}}
			transition={{ duration: 0.3, ease: "easeInOut" }}
			className="relative flex flex-col border-r bg-gradient-to-b from-green-600 to-green-700 text-white"
		>
			<div className="flex h-16 items-center justify-center border-b border-green-700">
				{!collapsed ? (
					<motion.h1
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						exit={{ opacity: 0 }}
						className="text-lg font-bold"
					>
						GreenMind
					</motion.h1>
				) : (
					<motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.2 }}>
						<Sprout className="h-8 w-8" />
					</motion.div>
				)}
			</div>
			<div className="flex-1 overflow-y-auto py-6">
				<nav className="flex flex-col gap-2 px-3">
					{sidebarItems.map((item) => {
						const isActive = pathname === item.href

						return (
							<Link
								key={item.href}
								href={item.href}
								className={cn(
									"group flex items-center gap-3 rounded-lg px-3 py-2 transition-all duration-300 hover:bg-white/10",
									isActive ? "bg-white/20 text-white" : "text-green-100",
								)}
							>
								<div className={cn("sidebar-icon", isActive && "active")}>
									<item.icon className="h-5 w-5" />
									{collapsed && <span className="sidebar-tooltip">{item.title}</span>}
								</div>
								{!collapsed && (
									<motion.span
										initial={!mounted ? { opacity: 1 } : { opacity: 0 }}
										animate={{ opacity: 1 }}
										transition={{ duration: 0.2, delay: 0.1 }}
									>
										{item.title}
									</motion.span>
								)}
							</Link>
						)
					})}
				</nav>
			</div>
			<Button
				variant="secondary"
				size="icon"
				className="absolute -right-3 top-20 z-10 flex h-6 w-6 items-center justify-center rounded-full border bg-white text-green-600 shadow-md"
				onClick={() => setCollapsed(!collapsed)}
			>
				{collapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
			</Button>
		</motion.aside>
	)
}
