[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Songpa-gu"]->.inner;
(
  nwr["leisure"="golf_course"](area.inner)(area.outer);
);
out geom;
