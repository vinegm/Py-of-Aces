# Maintainer: vinegm <info AT vinegm D0T com>
pkgname='py-of-aces'
pkgver=1.0.0
pkgrel=1
pkgdesc="A blackjack TUI written in Python"
arch=('x86_64')
url="https://github.com/vinegm/Py-of-Aces"
license=('MIT')
depends=('python' 'python-blessed')
makedepends=('python-build' 'python-installer' 'git')
source=('git+https://github.com/vinegm/Py-of-Aces.git#branch=main')
sha256sums=('SKIP')

build() {
    cd "$srcdir/Py-of-Aces"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/Py-of-Aces"
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}

