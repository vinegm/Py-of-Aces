# Maintainer: vinegm <info AT vinegm D0T com>
pkgname='py-of-aces'
pkgver=1.0.1
pkgrel=1
pkgdesc="A blackjack TUI written in Python"
arch=('x86_64')
url="https://github.com/vinegm/Py-of-Aces"
license=('MIT')
depends=('python' 'python-blessed')
makedepends=('python-build' 'python-installer' 'git')
source=("https://github.com/vinegm/Py-of-Aces/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('35eba37b2971fcb2fb39a8472bcdc464f6dd9e14b0c117b09930cfe032c5988d')

build() {
    cd "$srcdir/Py-of-Aces-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/Py-of-Aces-${pkgver}"
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}

