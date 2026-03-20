[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Atsuta Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
