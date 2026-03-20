[out:json][timeout:30];
area["name:ja"="福岡市"]->.outer;
area["name:en"="Fukuoka"]->.inner;
(
  nwr["tourism"="theme_park"](area.inner)(area.outer);
);
out geom;
