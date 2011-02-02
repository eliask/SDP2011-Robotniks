class Message {

    public boolean reset = false;
    public boolean kick = false;
    public int drive1_dir = 0;
    public int drive2_dir = 0;
    public int drive1_speed = 0;
    public int drive2_speed = 0;

    public int turn1_dir = 0;
    public int turn2_dir = 0;
    public int turn1_speed = 0;
    public int turn2_speed = 0;

    private int MotorPrecision = 4;
    private int drive1, drive2;
    private int turn1, turn2;

    void Message() {
        drive1_dir = 0;
        drive2_dir = 0;
        drive1_speed = 0;
        drive2_speed = 0;

        drive1_dir = 0;
        drive2_dir = 0;
        drive1_speed = 0;
        drive2_speed = 0;
    }

    void decode(int message) {
        reset = ( (message & 1) > 0 );
        kick = ( (message & 2) > 0 );

        drive1 = message & ( (1<<3)-1 << 2 );
        drive2 = message & ( (1<<3)-1 << 5 );
        turn1 = message & ( (1<<3)-1 << 8 );
        turn2 = message & ( (1<<3)-1 << 11 );

        drive1_dir = drive1 & MotorPrecision;
        drive2_dir = drive2 & MotorPrecision;
        drive1_speed = drive1 & (MotorPrecision-1);
        drive2_speed = drive2 & (MotorPrecision-1);

        turn1_dir = turn1 & MotorPrecision;
        turn2_dir = turn2 & MotorPrecision;
        turn1_speed = turn1 & (MotorPrecision-1);
        turn2_speed = turn2 & (MotorPrecision-1);
    }

}
