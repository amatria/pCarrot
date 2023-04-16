DROP TABLE IF EXISTS `pcarrot_news`;

CREATE TABLE IF NOT EXISTS `pcarrot_news` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(64) NOT NULL,
    `body` TEXT NOT NULL,
    `date` DATETIME NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

INSERT INTO `pcarrot_news` (`title`, `body`, `date`) VALUES
('Welcome to pCarrot!', 'This news item was created automatically by the \
pCarrot installer. You can delete it from the admin panel. You can create new \
news items from the admin panel, too.\n\nI hope you enjoy using pCarrot!', NOW());
