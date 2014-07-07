package com.skinry.app;

import android.app.ActionBar;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.view.ViewPager;
import android.support.v4.view.ViewPager.OnPageChangeListener;
import android.util.Log;
import android.view.View;
import android.widget.Button;

import com.flurry.android.FlurryAgent;
import com.skinry.app.custom.CustomActivity;
import com.skinry.app.ui.History;
import com.skinry.app.ui.HomeActivity;
import com.skinry.app.ui.Workout;
import com.skinry.app.utils.Const;

public class MainActivity extends CustomActivity
{


   int last_page = 0;

	private ViewPager pager;

	private View currentTab;

    private SharedPreferences mPrefs;


    @Override
    protected void onStart() {
        super.onStart();
        FlurryAgent.onStartSession(this, Const.FLURRY_API_KEY);
        setupActionBar();
        initTabs();
        initPager();
        FlurryAgent.logEvent("APP_START");
    }

    @Override
    protected void onStop() {
        super.onStop();
        Log.d("kmp", "omg");
        FlurryAgent.onEndSession(this);
    }



	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
        mPrefs = getPreferences(MODE_PRIVATE);
	}


	protected void setupActionBar() {
		final ActionBar actionBar = getActionBar();
		actionBar.setDisplayShowTitleEnabled(true);
		actionBar.setNavigationMode(ActionBar.NAVIGATION_MODE_STANDARD);
		actionBar.setDisplayUseLogoEnabled(true);
		actionBar.setLogo(R.drawable.icon);
		actionBar.setDisplayHomeAsUpEnabled(false);
		actionBar.setHomeButtonEnabled(false);
	}


	private void initTabs()
	{
		findViewById(R.id.tab1).setOnClickListener(this);
		findViewById(R.id.tab2).setOnClickListener(this);
		findViewById(R.id.tab3).setOnClickListener(this);
		setCurrentTab(0);
	}

    @Override
    public void onSaveInstanceState(Bundle savedInstanceState) {
        super.onSaveInstanceState(savedInstanceState);
        Log.d("kmp", "saving");
        savedInstanceState.putInt("MyInt", last_page);
    }

    @Override
    protected void onRestoreInstanceState (Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        Log.d("kmp", "restoring");
        if (savedInstanceState != null) {
            last_page = savedInstanceState.getInt("MyInt");
        } else {
            last_page = 0;
        }
    }


	@Override
	public void onClick(View v)
	{
		super.onClick(v);
		if (v.getId() == R.id.tab1) {
            last_page = 0;
			pager.setCurrentItem(0, true);
            FlurryAgent.logEvent("HOME_CLICK");
        }
		else if (v.getId() == R.id.tab2) {
            last_page = 1;
			pager.setCurrentItem(1, true);
            FlurryAgent.logEvent("HISTORY_CLICK");
        }
		else if (v.getId() == R.id.tab3) {
            last_page = 2;
			pager.setCurrentItem(2, true);
            FlurryAgent.logEvent("ABOUT_CLICK");
        }
	}

	private void setCurrentTab(int page)
	{
        Log.d("kmp some", Integer.toString(page));
        last_page = page;
		if (currentTab != null)
			currentTab.setEnabled(true);
		if (page == 0)
			currentTab = findViewById(R.id.tab1);
		else if (page == 1)
			currentTab = findViewById(R.id.tab2);
		else if (page == 2)
			currentTab = findViewById(R.id.tab3);
		currentTab.setEnabled(false);
		getActionBar().setTitle(((Button)currentTab).getText().toString());
	}


	private void initPager()
	{
		pager = (ViewPager) findViewById(R.id.pager);
		pager.setOnPageChangeListener(new OnPageChangeListener() {

			@Override
			public void onPageSelected(int page)
			{
				setCurrentTab(page);
			}

			@Override
			public void onPageScrolled(int arg0, float arg1, int arg2)
			{
			}

			@Override
			public void onPageScrollStateChanged(int arg0)
			{
			}
		});
		pager.setAdapter(new DummyPageAdapter(getSupportFragmentManager()));
	}


	private class DummyPageAdapter extends FragmentPagerAdapter
	{
		public DummyPageAdapter(FragmentManager fm)
		{
			super(fm);
		}


        @Override
        public int getItemPosition(Object object) {
                return POSITION_NONE;

        }



		@Override
		public Fragment getItem(int pos)
		{
			if (pos == 0)
				return new HomeActivity();
			if (pos == 1)
				return new History();
			return new Workout();
		}

		@Override
		public int getCount()
		{
			return 3;
		}
	}


    @Override
    public void onResume() {
        super.onResume();
        Log.d("kmp", "that"+Integer.toString(last_page));
        last_page = mPrefs.getInt("last_page", 0);
        //initPager();
        //pager.setAdapter(new DummyPageAdapter(getSupportFragmentManager()));
        /*initTabs();
        if (last_page == 0) {
            onClick(findViewById(R.id.tab1));
        } else if (last_page == 1) {
            onClick(findViewById(R.id.tab2));
        } else {
            onClick(findViewById(R.id.tab3));
        }*/
        //setCurrentTab(last_page);
        pager.setCurrentItem(last_page);

    }

    @Override
    public void onPause() {
        super.onPause();
        last_page = pager.getCurrentItem();
        Log.d("kmp", "this " + Integer.toString(last_page));
        SharedPreferences.Editor ed = mPrefs.edit();
        ed.putInt("last_page", last_page);
        ed.commit();
    }


}
