'use client';

import { ConnectButton } from '@rainbow-me/rainbowkit';
import Link from 'next/link';
import { ThemeToggle } from './ThemeToggle';


export function Header() {
    return (
        <header className="header">
            <Link href="/" className="logo" aria-label="RoboBazaar Home">
                <img src="/assets/logo-v2.svg" alt="RoboBazaar" style={{ height: 42, display: 'block' }} />
            </Link>

            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <ConnectButton.Custom>
                    {({ account, chain, mounted, openAccountModal, openChainModal, openConnectModal }) => {
                        const ready = mounted;
                        const connected = ready && account && chain;

                        if (!ready) {
                            return (
                                <button className="btn-premium btn-ghost" style={{ height: 36, padding: '0 14px' }} disabled>
                                    Connect
                                </button>
                            );
                        }

                        if (!connected) {
                            return (
                                <button
                                    className="btn-premium btn-primary"
                                    style={{ height: 36, padding: '0 14px' }}
                                    onClick={openConnectModal}
                                    type="button"
                                >
                                    Connect Wallet
                                </button>
                            );
                        }

                        return (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                <button className="tag" type="button" onClick={openChainModal}>
                                    <svg className="icon-svg" aria-hidden="true">
                                        <use href="#icon-wallet-v2" />
                                    </svg>
                                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{chain.name}</span>
                                </button>
                                <button className="tag" type="button" onClick={openAccountModal}>
                                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{account.displayName}</span>
                                </button>
                            </div>
                        );
                    }}
                </ConnectButton.Custom>

                <ThemeToggle />
            </div>
        </header>
    );
}
