package edu.campus.recycle.integration;

import edu.campus.recycle.entity.User;
import edu.campus.recycle.exception.AccountLockedException;
import edu.campus.recycle.exception.AuthenticationException;
import edu.campus.recycle.exception.DuplicateEntityException;
import edu.campus.recycle.service.UserService;
import edu.campus.recycle.support.TestDatabase;
import edu.campus.recycle.util.DaoFactory;
import edu.campus.recycle.util.ServiceFactory;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.api.parallel.Isolated;

import java.nio.file.Path;
import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;

@Isolated
class UserServiceTest {
    private static final String PASSWORD = "LocalTest123";
    private final UserService users = ServiceFactory.getInstance().getUserService();
    private final DaoFactory dao = DaoFactory.getInstance();
    @TempDir Path temp;
    private TestDatabase database;

    @BeforeEach
    void initializeDatabase() {
        database = new TestDatabase(temp);
    }

    @AfterEach
    void restoreDatabase() {
        if (database != null) {
            database.close();
        }
    }

    @Test
    void registerStoresDigestAndLoginReturnsAccount() {
        User created = register();
        User stored = users.findById(created.getId());
        var result = users.login(created.getUsername(), PASSWORD);
        assertEquals("STUDENT", stored.getRole());
        assertEquals(100, stored.getCreditScore());
        assertNotEquals(PASSWORD, stored.getPasswordHash());
        assertTrue(result.isSuccess());
        assertEquals(created.getId(), result.getUserId());
    }

    @Test
    void rejectsDuplicateUsernameWithoutCreatingSecondUser() {
        User created = register();
        var error = assertThrows(DuplicateEntityException.class,
                () -> users.register(created.getUsername(), PASSWORD, "测试学生", "20260002", null, null, null));
        assertEquals("DUP-001", error.getCode());
        assertEquals(1, dao.getUserDao().findAll().size());
    }

    @Test
    void fifthConsecutiveFailureLocksEvenWithCorrectPassword() {
        User user = register();
        for (int attempt = 1; attempt <= 4; attempt++) {
            var error = assertThrows(AuthenticationException.class, () -> users.login(user.getUsername(), "wrong"));
            assertEquals("AUTH-001", error.getCode());
            assertEquals(attempt, users.findById(user.getId()).getFailCount());
        }
        LocalDateTime earliestExpiry = LocalDateTime.now().withNano(0).plusMinutes(15);
        var lock = assertThrows(AccountLockedException.class, () -> users.login(user.getUsername(), "wrong"));
        assertEquals("LOCK-001", lock.getCode());
        User locked = users.findById(user.getId());
        assertEquals(5, locked.getFailCount());
        assertFalse(locked.getLockedUntil().isBefore(earliestExpiry));
        assertFalse(locked.getLockedUntil().isAfter(LocalDateTime.now().plusMinutes(15)));
        assertThrows(AccountLockedException.class, () -> users.login(user.getUsername(), PASSWORD));
    }

    @Test
    void successfulLoginResetsFailureCounterAfterLockExpires() {
        User user = register();
        dao.getUserDao().updateFailCount(user.getId(), 5, LocalDateTime.now().minusMinutes(1));
        assertTrue(users.login(user.getUsername(), PASSWORD).isSuccess());
        User stored = users.findById(user.getId());
        assertEquals(0, stored.getFailCount());
        assertNull(stored.getLockedUntil());
        assertNotNull(stored.getLastLoginAt());
    }

    @Test
    void passwordChangeAcceptsOnlyTheNewPasswordAndRotatesSalt() {
        User user = register();
        String newPassword = "UpdatedTest123";
        users.changePassword(user.getId(), PASSWORD, newPassword);
        assertThrows(AuthenticationException.class, () -> users.login(user.getUsername(), PASSWORD));
        assertTrue(users.login(user.getUsername(), newPassword).isSuccess());
        assertNotEquals(user.getSalt(), users.findById(user.getId()).getSalt());
    }

    @Test
    void creditUpdatesApplyBoundsAndKeepSnapshots() {
        User user = register();
        users.updateCredit(user.getId(), 80, null, "测试上限");
        assertEquals(150, users.findById(user.getId()).getCreditScore());
        users.updateCredit(user.getId(), -200, null, "测试下限");
        assertEquals(0, users.findById(user.getId()).getCreditScore());

        var snapshots = dao.getCreditLogDao().findByUserId(user.getId(), 10);
        assertEquals(2, snapshots.size());
        assertTrue(snapshots.stream().anyMatch(log -> log.getDelta() == 50 && log.getScoreAfter() == 150));
        assertTrue(snapshots.stream().anyMatch(log -> log.getDelta() == -150 && log.getScoreAfter() == 0));
    }

    private User register() {
        return users.register("student_test", PASSWORD, "测试学生", "20260001", null, null, null);
    }
}
