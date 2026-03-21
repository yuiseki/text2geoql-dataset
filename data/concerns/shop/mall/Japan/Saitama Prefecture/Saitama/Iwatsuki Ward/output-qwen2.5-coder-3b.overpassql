[out:json][timeout:30];
area["name:en"="Iwatsuki Ward"]->.outer;
area["name:en"="Saitama"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
