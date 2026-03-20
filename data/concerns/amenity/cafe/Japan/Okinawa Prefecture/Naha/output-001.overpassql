[out:json][timeout:30];
area["name:en"="Okinawa Prefecture"]->.outer;
area["name:en"="Naha"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
