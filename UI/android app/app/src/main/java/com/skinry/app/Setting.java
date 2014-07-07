package com.skinry.app;

import android.app.ActionBar;
import android.os.Bundle;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.skinry.app.custom.CustomActivity;

/**
 * The Activity Setting is launched when you taps on Setting icon on ActionBar in MainActivity.
 * It shows the custom useful layout components like custom SeekBar that you can use in your application layouts. 
 * 
 */
public class Setting extends CustomActivity
{

	/** Check if the app is running. */
	private boolean isRunning;


	/* (non-Javadoc)
	 * @see com.newsfeeder.custom.CustomActivity#onCreate(android.os.Bundle)
	 */
	@Override
	protected void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.settings);

		setupActionBar();
		setDummyContents();
	}

	/**
	 * This method will setup the top title bar (Action bar) content and display
	 * values. It will also setup the custom background theme for ActionBar. You
	 * can override this method to change the behavior of ActionBar for
	 * particular Activity
	 */
	protected void setupActionBar()
	{
		final ActionBar actionBar = getActionBar();
		actionBar.setDisplayShowTitleEnabled(true);
		actionBar.setTitle("Settings");
		actionBar.setNavigationMode(ActionBar.NAVIGATION_MODE_STANDARD);
		actionBar.setDisplayUseLogoEnabled(true);
		actionBar.setLogo(R.drawable.icon);
		actionBar.setDisplayHomeAsUpEnabled(true);
		actionBar.setHomeButtonEnabled(true);
	}

	/* (non-Javadoc)
	 * @see android.support.v4.app.FragmentActivity#onDestroy()
	 */
	@Override
	protected void onDestroy()
	{
		super.onDestroy();
		isRunning = false;
	}

	/**
	 * Sets the dummy contents for views. You can remove this method or can
	 * customize this method as per your needs. The thread in this method simply
	 * used to create a progress bar effect for Progress bar.
	 */
	private void setDummyContents()
	{
		isRunning = true;
		setTouchNClick(R.id.btnDemo);

		new Thread(new Runnable() {
			@Override
			public void run()
			{
				final ProgressBar pBar = (ProgressBar) findViewById(R.id.progressBar1);
				final TextView lbl1 = (TextView) findViewById(R.id.lblProgress1);
				final TextView lbl2 = (TextView) findViewById(R.id.lblProgress2);
				while (isRunning)
				{
					try
					{
						Thread.sleep(1000);
					} catch (Exception e)
					{
						e.printStackTrace();
					}
					runOnUiThread(new Runnable() {
						@Override
						public void run()
						{
							int p = pBar.getProgress() + 5;
							if (p > 100)
								p = 0;
							pBar.setProgress(p);
							lbl1.setText(p + "MB/100MB");
							lbl2.setText(p + "%");
						}
					});
				}
			}
		}).start();
	}

}
