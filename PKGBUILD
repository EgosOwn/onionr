url="https://onionr.net/"
pkgname="onionr"
pkgver=0.0.0
pkgrel=1
pkgdesc="P2P anonymous storage network"
arch=("x86_64")
license=('GPL')
source=("onionr-${pkgver}::git+https://gitlab.com/beardog/onionr.git#branch=master")
md5sums=('SKIP')
makedepends=('git' 'python' 'python-pip')
depends=('tor' 'python' 'python-pip')

build() {
        cd "$pkgname-${pkgver}"
        cd install
        ./install_arch.sh
}

package() {
        cd "$pkgname-${pkgver}"
        # make install
}
