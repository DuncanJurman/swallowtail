import { Metadata } from 'next'
import SettingsPageClient from './page-client'

export const metadata: Metadata = {
  title: 'Instance Settings - Swallowtail',
  description: 'Manage your instance settings and platform connections',
}

interface SettingsPageProps {
  params: Promise<{
    id: string
  }>
}

export default async function SettingsPage({ params }: SettingsPageProps) {
  const { id } = await params
  return <SettingsPageClient instanceId={id} />
}