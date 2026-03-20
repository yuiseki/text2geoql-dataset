[out:json][timeout:30];
area["name:ja"="名古屋市"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["tourism"="theme_park"](area.inner)(area.outer);
);
out geom;
