/* 图像池：循环复用Image实例以控制并发数量 */
export function ImagePool(size) {
    this.size = size // 容量上限
    this.images = [] // 已创建的Image集合
    this.counter = 0 // 轮询计数器
}

ImagePool.prototype.next = function () {
    if (this.images.length < this.size) {
        var image = new Image() // 新建Image
        this.images.push(image) // 加入池
        return image // 返回新建实例
    } else {
        if (this.counter >= this.size) {
            // Reset for unlikely but theoretically possible overflow.
            this.counter = 0 // 防溢出重置
        }
    }

    return this.images[this.counter++ % this.size] // 轮询返回池内实例
}