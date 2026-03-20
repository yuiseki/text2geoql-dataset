[out:json][timeout:30];
area["name:ja"="新潟市"]->.outer;
area["name:en"="Niigata"]->.inner;
(
  nwr["tourism"="theme_park"](area.inner)(area.outer);
);
out geom;
