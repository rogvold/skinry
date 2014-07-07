package com.skinry.app.ui;

import android.app.ActionBar;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Toast;

import com.flurry.android.FlurryAgent;
import com.skinry.app.R;
import com.skinry.app.utils.Const;

public class AdsActivity extends Activity {



    @Override
    protected void onStart() {
        super.onStart();
        FlurryAgent.onStartSession(this, Const.FLURRY_API_KEY);
    }

    @Override
    protected void onStop() {
        super.onStop();
        FlurryAgent.onEndSession(this);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setupActionBar();
        setContentView(R.layout.activity_ads);
        FlurryAgent.logEvent("WANT_SKIN_CLEAN_CLICKED");
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.ads, menu);
        return true;
    }

/*    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            return true;
        }
        return super.onOptionsItemSelected(item);
    }*/

    protected void setupActionBar() {
        final ActionBar actionBar = getActionBar();
        actionBar.setDisplayShowTitleEnabled(true);
        actionBar.setNavigationMode(ActionBar.NAVIGATION_MODE_STANDARD);
        actionBar.setDisplayUseLogoEnabled(true);
        actionBar.setLogo(R.drawable.icon);
        actionBar.setDisplayHomeAsUpEnabled(true);
        actionBar.setHomeButtonEnabled(true);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                finish();

        }
        return true;
    }

    public void onClick(View v) {
        int id = v.getId();
        switch (id) {
            case R.id.rl1:
                FlurryAgent.logEvent("SUBSCRIBE_1_CLICKED");
                break;
            case R.id.rl2:
                FlurryAgent.logEvent("SUBSCRIBE_3_CLICKED");
                break;
            case R.id.rl3:
                FlurryAgent.logEvent("SUBSCRIBE_6_CLICKED");
                break;
        }
        final AlertDialog.Builder ad =  new AlertDialog.Builder(this);
        ad.setTitle(R.string.attention);
        ad.setPositiveButton(R.string.confirm_pay, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int which) {
                FlurryAgent.logEvent("CONFIRM_PAYMENT_CLICKED");
                int duration = Toast.LENGTH_SHORT;
                Context context = getApplicationContext();
                CharSequence text = getString(R.string.subscript_unabled);
                Toast toast = Toast.makeText(context, text, duration);
                toast.setGravity(Gravity.CENTER_VERTICAL, 0, 0);
                toast.show();

            }
        });
        ad.setNegativeButton(R.string.cancel, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int which) {
                FlurryAgent.logEvent("CANCEL_PAYMENT_CLICKED");
            }
        });
        ad.setMessage(R.string.ads_message);
        Log.d("new", "alala");
        ad.create().show();

    }
}
