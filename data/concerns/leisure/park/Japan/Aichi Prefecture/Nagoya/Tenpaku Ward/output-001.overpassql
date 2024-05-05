[out:json][timeout:30000];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Tenpaku Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
