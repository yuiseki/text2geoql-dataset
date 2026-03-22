[out:json][timeout:30];
area["name:en"="Andalusia"]->.outer;
area["name:en"="Seville"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;