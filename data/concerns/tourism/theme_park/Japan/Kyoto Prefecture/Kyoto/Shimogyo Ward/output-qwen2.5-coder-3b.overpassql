[out:json][timeout:30];
area["name:ja"="京都府"]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["tourism"="theme_park"](area.inner)(area.outer);
);
out geom;
