[out:json][timeout:30];
area["name:ja"="大阪市"]->.outer;
area["name:en"="Osaka"]->.inner;
(
  nwr["tourism"="theme_park"](area.inner)(area.outer);
);
out geom;
