-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema forum_dash_db
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `forum_dash_db` ;

-- -----------------------------------------------------
-- Schema forum_dash_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `forum_dash_db` DEFAULT CHARACTER SET utf8 ;
USE `forum_dash_db` ;

-- -----------------------------------------------------
-- Table `forum_dash_db`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_dash_db`.`users` ;

CREATE TABLE IF NOT EXISTS `forum_dash_db`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(45) NULL,
  `last_name` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  `password` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forum_dash_db`.`thoughts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_dash_db`.`thoughts` ;

CREATE TABLE IF NOT EXISTS `forum_dash_db`.`thoughts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `content` TEXT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thoughts_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_thoughts_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum_dash_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forum_dash_db`.`liked_thoughts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_dash_db`.`liked_thoughts` ;

CREATE TABLE IF NOT EXISTS `forum_dash_db`.`liked_thoughts` (
  `users_id` INT NOT NULL,
  `thoughts_id` INT NOT NULL,
  PRIMARY KEY (`users_id`, `thoughts_id`),
  INDEX `fk_users_has_thoughts_thoughts1_idx` (`thoughts_id` ASC) VISIBLE,
  INDEX `fk_users_has_thoughts_users1_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_thoughts_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `forum_dash_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_has_thoughts_thoughts1`
    FOREIGN KEY (`thoughts_id`)
    REFERENCES `forum_dash_db`.`thoughts` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
