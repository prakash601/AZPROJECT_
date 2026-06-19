import styles from './Footer.module.css'

const links = [
  {
    href: 'https://fair-gasoline-add.notion.site/About-Me-80fca8d7f8744f05a298019af9b04293?pvs=4',
    label: 'About me',
    kind: 'about',
  },
  { href: 'mailto:prakashsankhla0601@gmail.com', label: 'Email', kind: 'email' },
  {
    href: 'https://www.linkedin.com/in/prakash-sankhla/',
    label: 'LinkedIn',
    kind: 'linkedin',
  },
  {
    href: 'https://www.instagram.com/prakas.sankhla/',
    label: 'Instagram',
    kind: 'instagram',
  },
  { href: 'https://github.com/prakash601', label: 'GitHub', kind: 'github' },
]

const icons = {
  about: ['M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'],
  email: [
    'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  ],
  linkedin: [
    'M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6z',
    'M2 9h4v12H2z',
    'M4 4a2 2 0 100 4 2 2 0 000-4z',
  ],
  instagram: [
    'M7 2h10a5 5 0 015 5v10a5 5 0 01-5 5H7a5 5 0 01-5-5V7a5 5 0 015-5z',
    'M7 2v20M17 2v20M2 7h20M2 17h20M2 12h20',
  ],
  github: [
    'M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 00-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0020 4.77 5.07 5.07 0 0019.91 1S18.73.65 16 2.48a13.38 13.38 0 00-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 005 4.77a5.44 5.44 0 00-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 009 18.13V22',
  ],
}

function SocialIcon({ kind }) {
  const paths = icons[kind] || []
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths.map((d, i) => (
        <path key={i} d={d} />
      ))}
    </svg>
  )
}

export function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <p className={styles.copy}>
          © {new Date().getFullYear()} Problem Finder
        </p>
        <ul className={styles.links} aria-label="Social links">
          {links.map((l) => (
            <li key={l.kind}>
              <a
                href={l.href}
                {...(l.href.startsWith('http') ? {
                  target: '_blank',
                  rel: 'noopener noreferrer',
                } : {})}
                className={styles.link}
                aria-label={l.label}
                title={l.label}
              >
                <SocialIcon kind={l.kind} />
              </a>
            </li>
          ))}
        </ul>
      </div>
    </footer>
  )
}
