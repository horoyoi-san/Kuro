namespace GameLauncher
{
    partial class LauncherForm
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.ListBox fileListBox;
        private System.Windows.Forms.Button downloadButton;
        private System.Windows.Forms.TextBox logBox;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.fileListBox = new System.Windows.Forms.ListBox();
            this.downloadButton = new System.Windows.Forms.Button();
            this.logBox = new System.Windows.Forms.TextBox();
            this.SuspendLayout();
            // 
            // fileListBox
            // 
            this.fileListBox.FormattingEnabled = true;
            this.fileListBox.ItemHeight = 16;
            this.fileListBox.Location = new System.Drawing.Point(12, 12);
            this.fileListBox.Name = "fileListBox";
            this.fileListBox.Size = new System.Drawing.Size(460, 196);
            this.fileListBox.TabIndex = 0;
            // 
            // downloadButton
            // 
            this.downloadButton.Location = new System.Drawing.Point(497, 12);
            this.downloadButton.Name = "downloadButton";
            this.downloadButton.Size = new System.Drawing.Size(106, 37);
            this.downloadButton.TabIndex = 1;
            this.downloadButton.Text = "ดาวน์โหลด";
            this.downloadButton.UseVisualStyleBackColor = true;
            this.downloadButton.Click += new System.EventHandler(this.downloadButton_Click);
            // 
            // logBox
            // 
            this.logBox.Location = new System.Drawing.Point(12, 228);
            this.logBox.Multiline = true;
            this.logBox.Name = "logBox";
            this.logBox.ReadOnly = true;
            this.logBox.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.logBox.Size = new System.Drawing.Size(591, 210);
            this.logBox.TabIndex = 2;
            // 
            // LauncherForm
            // 
            this.ClientSize = new System.Drawing.Size(615, 450);
            this.Controls.Add(this.logBox);
            this.Controls.Add(this.downloadButton);
            this.Controls.Add(this.fileListBox);
            this.Name = "LauncherForm";
            this.Text = "Game Launcher";
            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
}