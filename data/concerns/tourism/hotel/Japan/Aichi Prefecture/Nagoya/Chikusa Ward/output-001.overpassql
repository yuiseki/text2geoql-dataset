[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Chikusa Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
