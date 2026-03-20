[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["tourism"="theme_park"](area.inner)(area.outer);
);
out geom;
