[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:ja"="大阪市"]->.inner;
(
  nwr["tourism"="theme_park"](area.inner)(area.outer);
);
out geom;
