[out:json][timeout:30];
area["name:en"="Kosovo"]->.outer;
area["name:en"="Pristina"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
