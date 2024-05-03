// Important note: Hotal is not an amenity. "amenity"="hotel" is wrong!
[out:json][timeout:30000];
area["name:en"="Okinawa Prefecture"]->.outer;
area["name:en"="Naha"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
